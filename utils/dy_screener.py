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
        """计算背离信号 - 根据富途MRMC指标"""
        n = len(df)
        
        # 初始化列
        df['N1'] = 0  # 上次MACD<0以来的bar数
        df['MM1'] = 0  # 上次MACD>0以来的bar数
        
        # 计算N1和MM1 (BARSLAST)
        last_macd_neg = -1
        last_macd_pos = -1
        for i in range(n):
            if i > 0 and df['MACD'].iloc[i-1] >= 0 and df['MACD'].iloc[i] < 0:
                last_macd_neg = i
            if i > 0 and df['MACD'].iloc[i-1] <= 0 and df['MACD'].iloc[i] > 0:
                last_macd_pos = i
            df.loc[df.index[i], 'N1'] = i - last_macd_neg if last_macd_neg >= 0 else i
            df.loc[df.index[i], 'MM1'] = i - last_macd_pos if last_macd_pos >= 0 else i
        
        # 转换为整数
        df['N1'] = df['N1'].astype(int)
        df['MM1'] = df['MM1'].astype(int)
        
        # 计算底背离相关指标
        df['CC1'] = 0.0  # N1+1周期内的最低价(LLV)
        df['CC2'] = 0.0  # 往前推MM1+1的CC1
        df['CC3'] = 0.0  # 往前推MM1+1的CC2
        df['DIFL1'] = 0.0  # N1+1周期内的DIFF最低值
        df['DIFL2'] = 0.0  # 往前推MM1+1的DIFL1
        df['DIFL3'] = 0.0  # 往前推MM1+1的DIFL2
        
        for i in range(n):
            n1_val = int(df['N1'].iloc[i]) + 1
            mm1_val = int(df['MM1'].iloc[i]) + 1
            
            # CC1 = LLV(CLOSE, N1+1)
            start_idx = max(0, i - n1_val + 1)
            df.loc[df.index[i], 'CC1'] = df['Close'].iloc[start_idx:i+1].min()
            
            # DIFL1 = LLV(DIFF, N1+1)
            df.loc[df.index[i], 'DIFL1'] = df['DIFF'].iloc[start_idx:i+1].min()
            
            # CC2 = REF(CC1, MM1+1)
            if i >= mm1_val:
                df.loc[df.index[i], 'CC2'] = df['CC1'].iloc[i - mm1_val]
                df.loc[df.index[i], 'DIFL2'] = df['DIFL1'].iloc[i - mm1_val]
            
            # CC3 = REF(CC2, MM1+1)
            if i >= 2 * mm1_val:
                df.loc[df.index[i], 'CC3'] = df['CC2'].iloc[i - mm1_val]
                df.loc[df.index[i], 'DIFL3'] = df['DIFL2'].iloc[i - mm1_val]
        
        # 计算顶背离相关指标
        df['CH1'] = 0.0  # MM1+1周期内的最高价(HHV)
        df['CH2'] = 0.0  # 往前推N1+1的CH1
        df['CH3'] = 0.0  # 往前推N1+1的CH2
        df['DIFH1'] = 0.0  # MM1+1周期内的DIFF最高值
        df['DIFH2'] = 0.0  # 往前推N1+1的DIFH1
        df['DIFH3'] = 0.0  # 往前推N1+1的DIFH2
        
        for i in range(n):
            n1_val = int(df['N1'].iloc[i]) + 1
            mm1_val = int(df['MM1'].iloc[i]) + 1
            
            # CH1 = HHV(CLOSE, MM1+1)
            start_idx = max(0, i - mm1_val + 1)
            df.loc[df.index[i], 'CH1'] = df['Close'].iloc[start_idx:i+1].max()
            
            # DIFH1 = HHV(DIFF, MM1+1)
            df.loc[df.index[i], 'DIFH1'] = df['DIFF'].iloc[start_idx:i+1].max()
            
            # CH2 = REF(CH1, N1+1)
            if i >= n1_val:
                df.loc[df.index[i], 'CH2'] = df['CH1'].iloc[i - n1_val]
                df.loc[df.index[i], 'DIFH2'] = df['DIFH1'].iloc[i - n1_val]
            
            # CH3 = REF(CH2, N1+1)
            if i >= 2 * n1_val:
                df.loc[df.index[i], 'CH3'] = df['CH2'].iloc[i - n1_val]
                df.loc[df.index[i], 'DIFH3'] = df['DIFH1'].iloc[i - n1_val]
        
        # 底背离条件
        # AAA = ((CC1 < CC2) AND ((DIFL1 > DIFL2) AND ((REF(MACD,1) < 0) AND (DIFF < 0))))
        df['AAA'] = ((df['CC1'] < df['CC2']) & 
                     (df['DIFL1'] > df['DIFL2']) & 
                     (df['MACD'].shift(1) < 0) & 
                     (df['DIFF'] < 0))
        
        # BBB = ((CC1 < CC3) AND ((DIFL1 < DIFL2) AND ((DIFL1 > DIFL3) AND ((REF(MACD,1) < 0) AND (DIFF < 0)))))
        df['BBB'] = ((df['CC1'] < df['CC3']) & 
                     (df['DIFL1'] < df['DIFL2']) & 
                     (df['DIFL1'] > df['DIFL3']) & 
                     (df['MACD'].shift(1) < 0) & 
                     (df['DIFF'] < 0))
        
        # CCC = ((AAA OR BBB) AND (DIFF < 0))
        df['CCC'] = ((df['AAA'] | df['BBB']) & (df['DIFF'] < 0))
        
        # LLL = ((REF(CCC,1) = 0) AND CCC)
        df['LLL'] = (~df['CCC'].shift(1).fillna(False)) & df['CCC']
        
        # JJJ = (REF(CCC,1) AND (ABS(REF(DIFF,1)) >= (ABS(DIFF) * 1.01)))
        df['JJJ'] = df['CCC'].shift(1) & (df['DIFF'].shift(1).abs() >= (df['DIFF'].abs() * 1.01))
        
        # 顶背离条件
        # ZJDBL = ((CH1 > CH2) AND ((DIFH1 < DIFH2) AND ((REF(MACD,1) > 0) AND (DIFF > 0))))
        df['ZJDBL'] = ((df['CH1'] > df['CH2']) & 
                       (df['DIFH1'] < df['DIFH2']) & 
                       (df['MACD'].shift(1) > 0) & 
                       (df['DIFF'] > 0))
        
        # GXDBL = ((CH1 > CH3) AND ((DIFH1 > DIFH2) AND ((DIFH1 < DIFH3) AND ((REF(MACD,1) > 0) AND (DIFF > 0)))))
        df['GXDBL'] = ((df['CH1'] > df['CH3']) & 
                       (df['DIFH1'] > df['DIFH2']) & 
                       (df['DIFH1'] < df['DIFH3']) & 
                       (df['MACD'].shift(1) > 0) & 
                       (df['DIFF'] > 0))
        
        # DBBL = ((ZJDBL OR GXDBL) AND (DIFF > 0))
        df['DBBL'] = ((df['ZJDBL'] | df['GXDBL']) & (df['DIFF'] > 0))
        
        # DBL = ((REF(DBBL,1) = 0) AND (DBBL AND (DIFF > DEA)))
        df['DBL'] = (~df['DBBL'].shift(1).fillna(False)) & df['DBBL'] & (df['DIFF'] > df['DEA'])
        
        # DBJG = (REF(DBBL,1) AND (REF(DIFF,1) >= (DIFF * 1.01)))
        df['DBJG'] = df['DBBL'].shift(1) & (df['DIFF'].shift(1) >= (df['DIFF'] * 1.01))
        
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
        """计算买卖信号 - 根据富途MRMC指标完整逻辑
        
        买入信号：底背离后，DIFF开始收敛（JJJ）
        卖出信号：顶背离后，DIFF开始发散（DBJG）
        """
        if len(df) < 3:
            return False, False

        buy = False
        sell = False

        # 检查最近3天
        for i in range(1, min(4, len(df))):
            idx = -i
            
            # 买入信号：昨天JJJ=0 AND 今天JJJ=1
            # JJJ = 昨天CCC=1 AND |昨天DIFF| >= |今天DIFF| * 1.01
            if 'JJJ' in df.columns:
                jjj_today = df['CCC'].iloc[idx-1] if idx-1 >= -len(df) else False
                if jjj_today:
                    diff_yesterday = df['DIFF'].iloc[idx-1] if idx-1 >= -len(df) else 0
                    diff_today = df['DIFF'].iloc[idx]
                    jjj_today = jjj_today and (abs(diff_yesterday) >= abs(diff_today) * 1.01)
                
                jjj_yesterday = False
                if idx-2 >= -len(df) and 'JJJ' in df.columns:
                    ccc_prev = df['CCC'].iloc[idx-2] if idx-2 >= -len(df) else False
                    if ccc_prev:
                        diff_prev2 = df['DIFF'].iloc[idx-2] if idx-2 >= -len(df) else 0
                        diff_prev1 = df['DIFF'].iloc[idx-1] if idx-1 >= -len(df) else 0
                        jjj_yesterday = ccc_prev and (abs(diff_prev2) >= abs(diff_prev1) * 1.01)
                
                if jjj_today and not jjj_yesterday:
                    buy = True
            
            # 卖出信号：昨天DBJG=0 AND 今天DBJG=1
            # DBJG = 昨天DBBL=1 AND 昨天DIFF >= 今天DIFF * 1.01
            if 'DBJG' in df.columns:
                dbjg_today = df['DBBL'].iloc[idx-1] if idx-1 >= -len(df) else False
                if dbjg_today:
                    diff_yesterday = df['DIFF'].iloc[idx-1] if idx-1 >= -len(df) else 0
                    diff_today = df['DIFF'].iloc[idx]
                    dbjg_today = dbjg_today and (diff_yesterday >= diff_today * 1.01)
                
                dbjg_yesterday = False
                if idx-2 >= -len(df):
                    dbbl_prev = df['DBBL'].iloc[idx-2] if idx-2 >= -len(df) else False
                    if dbbl_prev:
                        diff_prev2 = df['DIFF'].iloc[idx-2] if idx-2 >= -len(df) else 0
                        diff_prev1 = df['DIFF'].iloc[idx-1] if idx-1 >= -len(df) else 0
                        dbjg_yesterday = dbbl_prev and (diff_prev2 >= diff_prev1 * 1.01)
                
                if dbjg_today and not dbjg_yesterday:
                    sell = True

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

            # 处理MultiIndex列（yfinance返回的数据可能有MultiIndex）
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # 计算指标
            df = self.calculate_bands(df)
            df = self.calculate_macd(df)
            df = self.calculate_divergence_signals(df)

            # 计算信号
            trend_signals = self.calculate_trend_signals(df)
            buy, sell = self.calculate_buy_sell_signals(df)

            # 获取最新数据
            latest = df.iloc[-1]
            
            # 计算交易额
            volume_usd = latest['Close'] * latest['Volume']

            return {
                'symbol': symbol,
                'price': latest['Close'],
                'volume_usd': volume_usd,
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
        for symbol in symbols:
            try:
                if self.filter_stock(symbol):
                    filtered_symbols.append(symbol)
            except Exception as e:
                # 忽略错误，继续下一个
                pass
        
        print(f"过滤完成，剩余 {len(filtered_symbols)} 只股票")

        if not filtered_symbols:
            return pd.DataFrame()

        # 第二步：分析股票
        print("第二步：计算技术指标...")
        for i, symbol in enumerate(filtered_symbols, 1):
            try:
                result = self.analyze_stock(symbol)
                if result:
                    results.append(result)
                if i % 10 == 0:
                    print(f"已分析 {i}/{len(filtered_symbols)} 只股票")
            except Exception as e:
                # 忽略错误，继续下一个
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
