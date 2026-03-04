"""
DY 策略回测引擎
支持单策略和多策略组合回测
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import yfinance as yf
from .dy_screener import DYScreener


class BacktestEngine:
    """回测引擎"""

    def __init__(self, initial_capital: float = 100000, commission: float = 0.001):
        """
        初始化回测引擎

        Args:
            initial_capital: 初始资金
            commission: 手续费率（默认 0.1%）
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.screener = DYScreener()

    def backtest_single_stock(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategy: str = 'buy_signal'
    ) -> Dict:
        """
        回测单个股票

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            strategy: 策略类型 ('buy_signal', 'stable', 'strongest')

        Returns:
            回测结果字典
        """
        try:
            # 下载数据
            df = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if df.empty or len(df) < 100:
                return None

            # 计算指标
            df = self.screener.calculate_bands(df)
            df = self.screener.calculate_macd(df)
            df = self.screener.calculate_divergence_signals(df)

            # 生成交易信号
            df = self._generate_signals(df, strategy)

            # 执行回测
            result = self._execute_backtest(df, symbol)

            return result

        except Exception as e:
            print(f"回测 {symbol} 失败: {e}")
            return None

    def _generate_signals(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """生成交易信号"""
        df['buy_signal'] = False
        df['sell_signal'] = False

        for i in range(1, len(df)):
            # 计算趋势信号
            close = df['Close'].iloc[i]
            close_prev = df['Close'].iloc[i-1]
            blue_top = df['blue_top'].iloc[i]
            blue_top_prev = df['blue_top'].iloc[i-1]
            blue_bottom = df['blue_bottom'].iloc[i]
            blue_bottom_prev = df['blue_bottom'].iloc[i-1]
            yellow_top = df['yellow_top'].iloc[i]
            yellow_top_prev = df['yellow_top'].iloc[i-1]

            up1 = close > blue_top and close_prev < blue_top_prev
            up3 = blue_bottom > yellow_top and blue_bottom_prev < yellow_top_prev
            down1 = close < blue_bottom and close_prev > blue_bottom_prev

            # MACD 信号
            diff_cross_up = (df['DIFF'].iloc[i-1] <= df['DEA'].iloc[i-1]) and (df['DIFF'].iloc[i] > df['DEA'].iloc[i])
            diff_cross_down = (df['DIFF'].iloc[i-1] >= df['DEA'].iloc[i-1]) and (df['DIFF'].iloc[i] < df['DEA'].iloc[i])

            # 底背离和顶背离
            lll = df['LLL'].iloc[i] if 'LLL' in df.columns else False
            dbl = df['DBL'].iloc[i] if 'DBL' in df.columns else False

            # 根据策略生成信号
            if strategy == 'buy_signal':
                # 激进策略：只要有买入信号
                df.loc[df.index[i], 'buy_signal'] = lll and diff_cross_up
            elif strategy == 'stable':
                # 稳健策略：买入 + UP1
                df.loc[df.index[i], 'buy_signal'] = lll and diff_cross_up and up1
            elif strategy == 'strongest':
                # 最强策略：买入 + UP3
                df.loc[df.index[i], 'buy_signal'] = lll and diff_cross_up and up3

            # 卖出信号
            df.loc[df.index[i], 'sell_signal'] = (dbl and diff_cross_down) or down1

        return df

    def _execute_backtest(self, df: pd.DataFrame, symbol: str) -> Dict:
        """执行回测"""
        capital = self.initial_capital
        position = 0  # 持仓数量
        trades = []  # 交易记录
        equity_curve = []  # 资金曲线

        for i in range(len(df)):
            date = df.index[i]
            price = df['Close'].iloc[i]

            # 买入信号
            if df['buy_signal'].iloc[i] and position == 0:
                # 全仓买入
                shares = int(capital / (price * (1 + self.commission)))
                cost = shares * price * (1 + self.commission)

                if shares > 0:
                    position = shares
                    capital -= cost
                    trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': price,
                        'shares': shares,
                        'cost': cost
                    })

            # 卖出信号
            elif df['sell_signal'].iloc[i] and position > 0:
                # 全部卖出
                proceeds = position * price * (1 - self.commission)
                capital += proceeds

                trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': price,
                    'shares': position,
                    'proceeds': proceeds
                })

                position = 0

            # 记录资金曲线
            current_value = capital + position * price
            equity_curve.append({
                'date': date,
                'equity': current_value,
                'position': position
            })

        # 如果还有持仓，按最后价格平仓
        if position > 0:
            final_price = df['Close'].iloc[-1]
            proceeds = position * final_price * (1 - self.commission)
            capital += proceeds
            trades.append({
                'date': df.index[-1],
                'type': 'SELL',
                'price': final_price,
                'shares': position,
                'proceeds': proceeds
            })

        # 计算统计指标
        final_capital = capital
        total_return = (final_capital - self.initial_capital) / self.initial_capital

        # 计算最大回撤
        equity_series = pd.Series([e['equity'] for e in equity_curve])
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min()

        # 计算胜率
        winning_trades = 0
        total_trades = len(trades) // 2  # 买卖成对

        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                if sell_trade['proceeds'] > buy_trade['cost']:
                    winning_trades += 1

        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        return {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'trades': trades,
            'equity_curve': equity_curve
        }

    def backtest_portfolio(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategy: str = 'buy_signal',
        max_positions: int = 5
    ) -> Dict:
        """
        回测投资组合

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            strategy: 策略类型
            max_positions: 最大持仓数量

        Returns:
            组合回测结果
        """
        results = []

        for symbol in symbols:
            result = self.backtest_single_stock(symbol, start_date, end_date, strategy)
            if result:
                results.append(result)

        if not results:
            return None

        # 计算组合统计
        total_return = np.mean([r['total_return'] for r in results])
        avg_win_rate = np.mean([r['win_rate'] for r in results])
        avg_max_drawdown = np.mean([r['max_drawdown'] for r in results])

        return {
            'strategy': strategy,
            'num_stocks': len(results),
            'avg_total_return': total_return,
            'avg_total_return_pct': total_return * 100,
            'avg_win_rate': avg_win_rate,
            'avg_win_rate_pct': avg_win_rate * 100,
            'avg_max_drawdown': avg_max_drawdown,
            'avg_max_drawdown_pct': avg_max_drawdown * 100,
            'individual_results': results
        }

    def compare_strategies(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategies: List[str] = None
    ) -> pd.DataFrame:
        """
        对比不同策略

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            strategies: 策略列表

        Returns:
            对比结果 DataFrame
        """
        if strategies is None:
            strategies = ['buy_signal', 'stable', 'strongest']

        results = []

        for strategy in strategies:
            result = self.backtest_single_stock(symbol, start_date, end_date, strategy)
            if result:
                results.append({
                    'strategy': strategy,
                    'total_return_pct': result['total_return_pct'],
                    'win_rate_pct': result['win_rate_pct'],
                    'max_drawdown_pct': result['max_drawdown_pct'],
                    'total_trades': result['total_trades']
                })

        return pd.DataFrame(results)


if __name__ == '__main__':
    # 示例：回测单个股票
    engine = BacktestEngine(initial_capital=100000)

    result = engine.backtest_single_stock(
        symbol='AAPL',
        start_date='2023-01-01',
        end_date='2024-01-01',
        strategy='stable'
    )

    if result:
        print(f"\n回测结果 - {result['symbol']}")
        print(f"初始资金: ${result['initial_capital']:,.2f}")
        print(f"最终资金: ${result['final_capital']:,.2f}")
        print(f"总收益率: {result['total_return_pct']:.2f}%")
        print(f"最大回撤: {result['max_drawdown_pct']:.2f}%")
        print(f"交易次数: {result['total_trades']}")
        print(f"胜率: {result['win_rate_pct']:.2f}%")
