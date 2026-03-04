"""
策略回测模块
用于测试不同策略在历史数据上的表现
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import yfinance as yf
from utils.dy_screener import DYScreener


class StrategyBacktest:
    """策略回测器"""

    def __init__(self, initial_capital: float = 100000):
        """
        初始化回测器

        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.screener = DYScreener()

    def backtest_strategy(
        self,
        symbols: List[str],
        strategy: str,
        start_date: str,
        end_date: str,
        position_size: float = 0.2,
        stop_loss: float = 0.08,
        take_profit: float = 0.15
    ) -> Dict:
        """
        回测单个策略

        Args:
            symbols: 股票列表
            strategy: 策略名称 ('aggressive', 'stable', 'strongest')
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'
            position_size: 单只股票仓位比例
            stop_loss: 止损比例
            take_profit: 止盈比例

        Returns:
            回测结果字典
        """
        trades = []
        capital = self.initial_capital
        positions = {}  # 当前持仓

        # 按日期遍历
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

        while current_date <= end_date_dt:
            date_str = current_date.strftime('%Y-%m-%d')

            # 检查持仓，处理止损止盈
            positions_to_close = []
            for symbol, position in positions.items():
                try:
                    # 获取当前价格
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(start=date_str, end=date_str)
                    if hist.empty:
                        continue

                    current_price = hist['Close'].iloc[0]
                    entry_price = position['entry_price']
                    pnl_pct = (current_price - entry_price) / entry_price

                    # 止损或止盈
                    if pnl_pct <= -stop_loss or pnl_pct >= take_profit:
                        exit_value = position['shares'] * current_price
                        pnl = exit_value - position['cost']
                        capital += exit_value

                        trades.append({
                            'symbol': symbol,
                            'entry_date': position['entry_date'],
                            'exit_date': date_str,
                            'entry_price': entry_price,
                            'exit_price': current_price,
                            'shares': position['shares'],
                            'pnl': pnl,
                            'pnl_pct': pnl_pct,
                            'reason': 'stop_loss' if pnl_pct <= -stop_loss else 'take_profit'
                        })

                        positions_to_close.append(symbol)

                except Exception:
                    continue

            # 清理已平仓的持仓
            for symbol in positions_to_close:
                del positions[symbol]

            # 检查新的买入信号
            if len(positions) < int(1 / position_size):  # 最大持仓数
                for symbol in symbols:
                    if symbol in positions:
                        continue

                    try:
                        # 获取历史数据用于计算信号
                        df = yf.download(
                            symbol,
                            start=(current_date - timedelta(days=180)).strftime('%Y-%m-%d'),
                            end=date_str,
                            progress=False
                        )

                        if df.empty or len(df) < 100:
                            continue

                        # 计算指标
                        df = self.screener.calculate_bands(df)
                        df = self.screener.calculate_macd(df)
                        df = self.screener.calculate_divergence_signals(df)

                        # 计算信号
                        trend_signals = self.screener.calculate_trend_signals(df)
                        buy, sell = self.screener.calculate_buy_sell_signals(df)

                        # 根据策略判断是否买入
                        should_buy = False
                        if strategy == 'aggressive' and buy:
                            should_buy = True
                        elif strategy == 'stable' and buy and trend_signals['up1']:
                            should_buy = True
                        elif strategy == 'strongest' and buy and trend_signals['up3']:
                            should_buy = True

                        if should_buy:
                            # 买入
                            entry_price = df['Close'].iloc[-1]
                            position_value = capital * position_size
                            shares = int(position_value / entry_price)

                            if shares > 0:
                                cost = shares * entry_price
                                capital -= cost

                                positions[symbol] = {
                                    'entry_date': date_str,
                                    'entry_price': entry_price,
                                    'shares': shares,
                                    'cost': cost
                                }

                    except Exception:
                        continue

            # 下一天
            current_date += timedelta(days=1)

        # 计算最终结果
        final_capital = capital
        for symbol, position in positions.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(start=end_date, end=end_date)
                if not hist.empty:
                    final_price = hist['Close'].iloc[0]
                    final_capital += position['shares'] * final_price
            except Exception:
                final_capital += position['cost']  # 按成本价计算

        # 统计
        total_trades = len(trades)
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        losing_trades = len([t for t in trades if t['pnl'] <= 0])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0

        total_pnl = sum([t['pnl'] for t in trades])
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        avg_win = sum([t['pnl'] for t in trades if t['pnl'] > 0]) / winning_trades if winning_trades > 0 else 0
        avg_loss = sum([t['pnl'] for t in trades if t['pnl'] <= 0]) / losing_trades if losing_trades > 0 else 0

        total_return = (final_capital - self.initial_capital) / self.initial_capital

        return {
            'strategy': strategy,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            'trades': trades
        }

    def compare_strategies(
        self,
        symbols: List[str],
        strategies: List[str],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        对比多个策略

        Args:
            symbols: 股票列表
            strategies: 策略列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            对比结果 DataFrame
        """
        results = []

        for strategy in strategies:
            print(f"回测策略: {strategy}...")
            result = self.backtest_strategy(symbols, strategy, start_date, end_date)
            results.append({
                '策略': strategy,
                '总收益率': f"{result['total_return_pct']:.2f}%",
                '交易次数': result['total_trades'],
                '胜率': f"{result['win_rate_pct']:.2f}%",
                '平均盈利': f"${result['avg_win']:.2f}",
                '平均亏损': f"${result['avg_loss']:.2f}",
                '盈亏比': f"{result['profit_factor']:.2f}",
                '最终资金': f"${result['final_capital']:.2f}"
            })

        return pd.DataFrame(results)


if __name__ == '__main__':
    # 示例：回测三种策略
    backtester = StrategyBacktest(initial_capital=100000)

    # 测试股票
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']

    # 回测时间范围（最近 6 个月）
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')

    print("=" * 60)
    print("策略回测")
    print("=" * 60)
    print(f"回测期间: {start_date} 至 {end_date}")
    print(f"初始资金: $100,000")
    print(f"测试股票: {', '.join(test_symbols)}")
    print("=" * 60)

    # 对比三种策略
    comparison = backtester.compare_strategies(
        symbols=test_symbols,
        strategies=['aggressive', 'stable', 'strongest'],
        start_date=start_date,
        end_date=end_date
    )

    print("\n策略对比结果:")
    print(comparison.to_string(index=False))
