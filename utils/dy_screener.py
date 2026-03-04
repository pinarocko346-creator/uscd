"""
DY 指标选股器 - 基于 TradingView Pine Script 逻辑
实现蓝黄带趋势判断和 MACD 背离信号
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')


class DYScreener:
    """DY 指标选股器"""

    def __init__(self, min_price: float = 0.1, min_volume_usd: float = 10_000_000):
        """
        初始化选股器

        Args:
            min_price: 最低价格（美元）
            min_volume_usd: 最低交易额（美元）
        """
        self.min_price = min_price
        self.min_volume_usd = min_volume_usd

    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """计算 EMA"""
        return data.ewm(span=period, adjust=False).mean()

    def calculate_bands(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算蓝带和黄带"""
        df['blue_top'] = self.calculate_ema(df['High'], 24)
        df['blue_bottom'] = self.calculate_ema(df['Low'], 23)
        df['yellow_top'] = self.calculate_ema(df['High'], 89)
        df['yellow_bottom'] = self.calculate_ema(df['Low'], 90)
        return df

    def calculate_macd(self, df: pd.DataFrame, short: int = 12, long: int = 26, signal: int = 9) -> pd.DataFrame:
        """计算 MACD"""
        fast_ma = self.calculate_ema(df['Close'], short)
        slow_ma = self.calculate_ema(df['Close'], long)
        df['DIFF'] = fast_ma - slow_ma
        df['DEA'] = self.calculate_ema(df['DIFF'], signal)
        df['MACD'] = (df['DIFF'] - df['DEA']) * 2
        return df

    def bars_since(self, condition: pd.Series) -> pd.Series:
        """计算自上次条件为真以来的 bar 数"""
        result = pd.Series(index=condition.index, dtype=float)
        last_true = -1
        for i in range(len(condition)):
            if condition.iloc[i]:
                last_true = i
            if last_true >= 0:
                result.iloc[i] = i - last_true
            else:
                result.iloc[i] = np.nan
        return result

    def calculate_divergence_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算背离信号"""
        # 计算 N1 和 MM1
        df['N1'] = self.bars_since((df['MACD'].shift(1) >= 0) & (df['MACD'] < 0))
        df['MM1'] = self.bars_since((df['MACD'].shift(1) <= 0) & (df['MACD'] > 0))

        # 填充无效值
        df['valid_N1'] = df['N1'].fillna(1).astype(int)
        df['valid_MM1'] = df['MM1'].fillna(1).astype(int)

        # 计算底背离相关指标
        df['CC1'] = df['Close'].rolling(window=1).apply(
            lambda x: df['Close'].iloc[max(0, len(df) - int(df['valid_N1'].iloc[-1]) - 1):].min()
            if len(df) > 0 else np.nan, raw=False
        )

        df['DIFL1'] = df['DIFF'].rolling(window=1).apply(
            lambda x: df['DIFF'].iloc[max(0, len(df) - int(df['valid_N1'].iloc[-1]) - 1):].min()
            if len(df) > 0 else np.nan, raw=False
        )

        # 简化的背离判断
        df['AAA'] = (
            (df['CC1'] < df['CC1'].shift(int(df['valid_MM1'].iloc[-1]) + 1)) &
            (df['DIFL1'] > df['DIFL1'].shift(int(df['valid_MM1'].iloc[-1]) + 1)) &
            (df['MACD'].shift(1) < 0) & (df['DIFF'] < 0)
        )

        df['CCC'] = df['AAA'] & (df['DIFF'] < 0)
        df['LLL'] = (~df['CCC'].shift(1).fillna(False)) & df['CCC']

        # 计算顶背离相关指标
        df['CH1'] = df['Close'].rolling(window=1).apply(
            lambda x: df['Close'].iloc[max(0, len(df) - int(df['valid_MM1'].iloc[-1]) - 1):].max()
            if len(df) > 0 else np.nan, raw=False
        )

        df['DIFH1'] = df['DIFF'].rolling(window=1).apply(
            lambda x: df['DIFF'].iloc[max(0, len(df) - int(df['valid_MM1'].iloc[-1]) - 1):].max()
            if len(df) > 0 else np.nan, raw=False
        )

        df['ZJDBL'] = (
            (df['CH1'] > df['CH1'].shift(int(df['valid_N1'].iloc[-1]) + 1)) &
            (df['DIFH1'] < df['DIFH1'].shift(int(df['valid_N1'].iloc[-1]) + 1)) &
            (df['MACD'].shift(1) > 0) & (df['DIFF'] > 0)
        )

        df['DBBL'] = df['ZJDBL'] & (df['DIFF'] > 0)
        df['DBL'] = (~df['DBBL'].shift(1).fillna(False)) & df['DBBL'] & (df['DIFF'] > df['DEA'])

        return df

    def calculate_trend_signals(self, df: pd.DataFrame) -> Dict[str, bool]:
        """计算趋势信号"""
        if len(df) < 2:
            return {
                'up1': False, 'up2': False, 'up3': False,
                'down1': False, 'down2': False, 'down3': False
            }

        close = df['Close'].iloc[-1]
        close_prev = df['Close'].iloc[-2]
        blue_top = df['blue_top'].iloc[-1]
        blue_top_prev = df['blue_top'].iloc[-2]
        blue_bottom = df['blue_bottom'].iloc[-1]
        blue_bottom_prev = df['blue_bottom'].iloc[-2]
        yellow_top = df['yellow_top'].iloc[-1]
        yellow_top_prev = df['yellow_top'].iloc[-2]
        yellow_bottom = df['yellow_bottom'].iloc[-1]
        yellow_bottom_prev = df['yellow_bottom'].iloc[-2]

        return {
            'up1': close > blue_top and close_prev < blue_top_prev,
            'up2': close > yellow_top and close_prev < yellow_top_prev,
            'up3': blue_bottom > yellow_top and blue_bottom_prev < yellow_top_prev,
            'down1': close < blue_bottom and close_prev > blue_bottom_prev,
            'down2': close < yellow_bottom and close_prev > yellow_bottom_prev,
            'down3': blue_bottom < yellow_bottom and blue_bottom_prev > yellow_bottom_prev
        }

    def calculate_buy_sell_signals(self, df: pd.DataFrame) -> Tuple[bool, bool]:
        """计算买卖信号"""
        if len(df) < 2:
            return False, False

        # 简化的买卖信号逻辑
        diff_cross_up = (df['DIFF'].iloc[-2] <= df['DEA'].iloc[-2]) and (df['DIFF'].iloc[-1] > df['DEA'].iloc[-1])
        diff_cross_down = (df['DIFF'].iloc[-2] >= df['DEA'].iloc[-2]) and (df['DIFF'].iloc[-1] < df['DEA'].iloc[-1])

        # 买入信号：底背离 + DIFF 上穿 DEA
        buy = df['LLL'].iloc[-1] and diff_cross_up if 'LLL' in df.columns else False

        # 卖出信号：顶背离 + DIFF 下穿 DEA
        sell = df['DBL'].iloc[-1] and diff_cross_down if 'DBL' in df.columns else False

        return buy, sell

    def filter_stock(self, symbol: str) -> bool:
        """过滤股票"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # 获取最新价格
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if current_price is None or current_price < self.min_price:
                return False

            # 获取交易量和价格计算交易额
            volume = info.get('volume') or info.get('regularMarketVolume')
            if volume is None:
                return False

            volume_usd = volume * current_price
            if volume_usd < self.min_volume_usd:
                return False

            return True

        except Exception:
            return False

    def analyze_stock(self, symbol: str, period: str = '6mo') -> Dict:
        """分析单个股票"""
        try:
            # 下载数据
            df = yf.download(symbol, period=period, progress=False)

            if df.empty or len(df) < 100:
                return None

            # 计算指标
            df = self.calculate_bands(df)
            df = self.calculate_macd(df)
            df = self.calculate_divergence_signals(df)

            # 计算信号
            trend_signals = self.calculate_trend_signals(df)
            buy, sell = self.calculate_buy_sell_signals(df)

            # 获取最新数据
            latest = df.iloc[-1]

            return {
                'symbol': symbol,
                'price': latest['Close'],
                'buy': buy,
                'sell': sell,
                **trend_signals
            }

        except Exception as e:
            return None

    def screen_stocks(self, symbols: List[str], max_workers: int = 10) -> pd.DataFrame:
        """筛选股票"""
        results = []

        print(f"开始筛选 {len(symbols)} 只股票...")

        # 第一步：过滤股票
        print("第一步：应用价格和交易量过滤...")
        filtered_symbols = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {executor.submit(self.filter_stock, symbol): symbol for symbol in symbols}
            for i, future in enumerate(as_completed(future_to_symbol), 1):
                symbol = future_to_symbol[future]
                try:
                    if future.result():
                        filtered_symbols.append(symbol)
                    if i % 50 == 0:
                        print(f"已过滤 {i}/{len(symbols)} 只股票，通过 {len(filtered_symbols)} 只")
                except Exception:
                    pass

        print(f"过滤完成，剩余 {len(filtered_symbols)} 只股票")

        # 第二步：分析股票
        print("第二步：计算技术指标...")
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {executor.submit(self.analyze_stock, symbol): symbol for symbol in filtered_symbols}
            for i, future in enumerate(as_completed(future_to_symbol), 1):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    if i % 10 == 0:
                        print(f"已分析 {i}/{len(filtered_symbols)} 只股票")
                except Exception:
                    pass

        print(f"分析完成，成功分析 {len(results)} 只股票")

        if not results:
            return pd.DataFrame()

        df_results = pd.DataFrame(results)
        return df_results


def get_us_stock_list() -> List[str]:
    """获取美股列表"""
    # 这里使用一些常见的美股列表
    # 实际应用中可以从更完整的数据源获取
    import requests

    try:
        # 获取 S&P 500 成分股
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        sp500 = tables[0]['Symbol'].tolist()

        # 获取 NASDAQ 100 成分股
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        tables = pd.read_html(url)
        nasdaq100 = tables[4]['Ticker'].tolist()

        # 合并并去重
        symbols = list(set(sp500 + nasdaq100))
        return symbols

    except Exception as e:
        print(f"获取股票列表失败: {e}")
        # 返回一些常见股票作为示例
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B',
            'UNH', 'JNJ', 'V', 'WMT', 'XOM', 'JPM', 'PG', 'MA', 'HD', 'CVX',
            'LLY', 'ABBV', 'MRK', 'KO', 'PEP', 'AVGO', 'COST', 'TMO', 'MCD'
        ]


if __name__ == '__main__':
    # 创建选股器
    screener = DYScreener(min_price=0.1, min_volume_usd=10_000_000)

    # 获取股票列表
    symbols = get_us_stock_list()
    print(f"获取到 {len(symbols)} 只股票")

    # 筛选股票
    results = screener.screen_stocks(symbols, max_workers=10)

    # 显示结果
    if not results.empty:
        print("\n=== 筛选结果 ===")
        print(f"总共找到 {len(results)} 只符合条件的股票\n")

        # 显示买入信号的股票
        buy_signals = results[results['buy'] == True]
        if not buy_signals.empty:
            print(f"\n买入信号 ({len(buy_signals)} 只):")
            print(buy_signals[['symbol', 'price', 'up1', 'up2', 'up3']].to_string(index=False))

        # 显示卖出信号的股票
        sell_signals = results[results['sell'] == True]
        if not sell_signals.empty:
            print(f"\n卖出信号 ({len(sell_signals)} 只):")
            print(sell_signals[['symbol', 'price', 'down1', 'down2', 'down3']].to_string(index=False))

        # 保存完整结果
        results.to_csv('dy_screener_results.csv', index=False)
        print(f"\n完整结果已保存到 dy_screener_results.csv")
    else:
        print("未找到符合条件的股票")
