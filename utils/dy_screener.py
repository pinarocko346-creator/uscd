#!/usr/bin/env python3
"""
DY策略选股器 - 核心类
实现完整的技术指标计算和信号判断逻辑
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class DYScreener:
    """DY策略选股器核心类"""
    
    def __init__(self):
        self.qualified_stocks = []
        
    def get_stock_data(self, symbol, period='1y'):
        """获取股票数据"""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(period=period)
            
            if df is None or len(df) < 100:
                return None
            
            df = df.reset_index()
            df.columns = [col.lower() for col in df.columns]
            
            return df
        except:
            return None
    
    def calculate_ema(self, series, period):
        """计算EMA"""
        return series.ewm(span=period, adjust=False).mean()
    
    def calculate_macd(self, close, short=12, long=26, signal=9):
        """计算MACD"""
        fast_ma = self.calculate_ema(close, short)
        slow_ma = self.calculate_ema(close, long)
        diff = fast_ma - slow_ma
        dea = self.calculate_ema(diff, signal)
        macd = (diff - dea) * 2
        return diff, dea, macd
    
    def bars_since_condition(self, condition_series):
        """计算自上次条件为True以来的K线数"""
        result = []
        bars_count = 0
        found_first = False
        
        for val in condition_series:
            if pd.isna(val):
                result.append(np.nan)
                continue
                
            if val:
                result.append(0)
                bars_count = 0
                found_first = True
            else:
                if found_first:
                    bars_count += 1
                    result.append(bars_count)
                else:
                    result.append(np.nan)
        
        return pd.Series(result, index=condition_series.index)
    
    def rolling_min_with_dynamic_window(self, series, window_series, default_window=1):
        """动态窗口的rolling min"""
        result = []
        for i in range(len(series)):
            window = int(window_series.iloc[i]) if not pd.isna(window_series.iloc[i]) else default_window
            window = max(1, min(window, i + 1))
            start_idx = max(0, i - window + 1)
            result.append(series.iloc[start_idx:i+1].min())
        return pd.Series(result, index=series.index)
    
    def rolling_max_with_dynamic_window(self, series, window_series, default_window=1):
        """动态窗口的rolling max"""
        result = []
        for i in range(len(series)):
            window = int(window_series.iloc[i]) if not pd.isna(window_series.iloc[i]) else default_window
            window = max(1, min(window, i + 1))
            start_idx = max(0, i - window + 1)
            result.append(series.iloc[start_idx:i+1].max())
        return pd.Series(result, index=series.index)
    
    def shift_by_series(self, series, shift_series, default_shift=1):
        """根据shift_series中的值动态shift"""
        result = []
        for i in range(len(series)):
            shift_val = int(shift_series.iloc[i]) if not pd.isna(shift_series.iloc[i]) else default_shift
            shift_val = max(0, shift_val)
            target_idx = i - shift_val
            if target_idx >= 0:
                result.append(series.iloc[target_idx])
            else:
                result.append(np.nan)
        return pd.Series(result, index=series.index)
    
    def calculate_trend_signals(self, df):
        """计算趋势信号（蓝黄带）"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # 蓝带和黄带
        blue_top = self.calculate_ema(high, 24)
        blue_bottom = self.calculate_ema(low, 23)
        yellow_top = self.calculate_ema(high, 89)
        yellow_bottom = self.calculate_ema(low, 90)
        
        # 趋势信号
        up1 = (close > blue_top) & (close.shift(1) < blue_top.shift(1))
        up2 = (close > yellow_top) & (close.shift(1) < yellow_top.shift(1))
        up3 = (blue_bottom > yellow_top) & (blue_bottom.shift(1) < yellow_top.shift(1))
        
        down1 = (close < blue_bottom) & (close.shift(1) > blue_bottom.shift(1))
        down2 = (close < yellow_bottom) & (close.shift(1) > yellow_bottom.shift(1))
        down3 = (blue_bottom < yellow_bottom) & (blue_bottom.shift(1) > yellow_bottom.shift(1))
        
        return up1, up2, up3, down1, down2, down3
    
    def calculate_divergence_signals(self, df):
        """计算背离信号（底背离LLL和顶背离DBL）"""
        close = df['close']
        
        # MACD
        diff, dea, macd = self.calculate_macd(close)
        
        # N1和MM1
        macd_cross_down = (macd.shift(1) >= 0) & (macd < 0)
        macd_cross_up = (macd.shift(1) <= 0) & (macd > 0)
        
        n1 = self.bars_since_condition(macd_cross_down).fillna(1)
        mm1 = self.bars_since_condition(macd_cross_up).fillna(1)
        
        # 底背离计算
        cc1 = self.rolling_min_with_dynamic_window(close, n1 + 1)
        cc2 = self.shift_by_series(cc1, mm1 + 1)
        cc3 = self.shift_by_series(cc2, mm1 + 1)
        
        difl1 = self.rolling_min_with_dynamic_window(diff, n1 + 1)
        difl2 = self.shift_by_series(difl1, mm1 + 1)
        difl3 = self.shift_by_series(difl2, mm1 + 1)
        
        aaa = (cc1 < cc2) & (difl1 > difl2) & (macd.shift(1) < 0) & (diff < 0)
        bbb = (cc1 < cc3) & (difl1 < difl2) & (difl1 > difl3) & (macd.shift(1) < 0) & (diff < 0)
        ccc = (aaa | bbb) & (diff < 0)
        
        lll = (~ccc.shift(1).fillna(False)) & ccc  # 底背离信号
        
        # 顶背离计算
        ch1 = self.rolling_max_with_dynamic_window(close, mm1 + 1)
        ch2 = self.shift_by_series(ch1, n1 + 1)
        ch3 = self.shift_by_series(ch2, n1 + 1)
        
        difh1 = self.rolling_max_with_dynamic_window(diff, mm1 + 1)
        difh2 = self.shift_by_series(difh1, n1 + 1)
        difh3 = self.shift_by_series(difh2, n1 + 1)
        
        zjdbl = (ch1 > ch2) & (difh1 < difh2) & (macd.shift(1) > 0) & (diff > 0)
        gxdbl = (ch1 > ch3) & (difh1 > difh2) & (difh1 < difh3) & (macd.shift(1) > 0) & (diff > 0)
        dbbl = (zjdbl | gxdbl) & (diff > 0)
        
        dbl = (~dbbl.shift(1).fillna(False)) & dbbl & (diff > dea)  # 顶背离信号
        
        # MACD金叉死叉
        diff_cross_up = (diff > dea) & (diff.shift(1) <= dea.shift(1))
        diff_cross_down = (diff < dea) & (diff.shift(1) >= dea.shift(1))
        
        return lll, dbl, diff, dea, diff_cross_up, diff_cross_down
    
    def filter_stock(self, symbol, min_price=0.10, min_volume_usd=10_000_000):
        """第一轮过滤：价格和成交额"""
        try:
            df = self.get_stock_data(symbol)
            if df is None or len(df) < 100:
                return False, None
            
            last_close = df['close'].iloc[-1]
            last_volume = df['volume'].iloc[-1]
            last_dollar_volume = last_close * last_volume
            
            if last_close < min_price or last_dollar_volume < min_volume_usd:
                return False, None
            
            return True, df
        except:
            return False, None
    
    def screen_stock(self, symbol):
        """完整筛选单只股票"""
        try:
            # 第一轮过滤
            passed, df = self.filter_stock(symbol)
            if not passed:
                return False, None
            
            # 计算趋势信号
            up1, up2, up3, down1, down2, down3 = self.calculate_trend_signals(df)
            
            # 计算背离信号
            lll, dbl, diff, dea, diff_cross_up, diff_cross_down = self.calculate_divergence_signals(df)
            
            # 买卖信号
            buy = lll & diff_cross_up
            sell = dbl & diff_cross_down
            
            # 检查最新信号
            last_idx = -1
            has_buy = bool(buy.iloc[last_idx])
            has_sell = bool(sell.iloc[last_idx])
            has_up1 = bool(up1.iloc[last_idx])
            has_up2 = bool(up2.iloc[last_idx])
            has_up3 = bool(up3.iloc[last_idx])
            has_down1 = bool(down1.iloc[last_idx])
            has_down2 = bool(down2.iloc[last_idx])
            has_down3 = bool(down3.iloc[last_idx])
            
            # 只保留有信号的股票
            if not any([has_buy, has_sell, has_up1, has_up2, has_up3, has_down1, has_down2, has_down3]):
                return False, None
            
            last_close = df['close'].iloc[-1]
            last_volume = df['volume'].iloc[-1]
            last_dollar_volume = last_close * last_volume
            
            return True, {
                'symbol': symbol,
                'price': float(last_close),
                'volume_usd': float(last_dollar_volume / 1_000_000),
                'buy': has_buy,
                'sell': has_sell,
                'up1': has_up1,
                'up2': has_up2,
                'up3': has_up3,
                'down1': has_down1,
                'down2': has_down2,
                'down3': has_down3,
                'diff': float(diff.iloc[last_idx]),
                'dea': float(dea.iloc[last_idx])
            }
        except Exception as e:
            return False, None
    
    def get_market_symbols(self):
        """获取市场股票列表（S&P 500 + NASDAQ 100）"""
        symbols = []
        
        # 尝试获取S&P 500
        try:
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            df = tables[0]
            sp500 = [s.replace('.', '-') for s in df['Symbol'].tolist()]
            symbols.extend(sp500)
        except:
            # 备用列表
            sp500_backup = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
                'UNH', 'JNJ', 'XOM', 'V', 'PG', 'JPM', 'MA', 'HD', 'CVX', 'MRK',
                'ABBV', 'PEP', 'KO', 'AVGO', 'COST', 'LLY', 'WMT', 'MCD', 'CSCO',
                'ACN', 'ABT', 'TMO', 'DHR', 'VZ', 'ADBE', 'NKE', 'CRM', 'NFLX',
                'ORCL', 'INTC', 'AMD', 'QCOM', 'TXN', 'CMCSA', 'PM', 'UNP', 'NEE',
                'HON', 'RTX', 'UPS', 'LOW', 'BA', 'SBUX', 'IBM', 'CAT', 'GE'
            ]
            symbols.extend(sp500_backup)
        
        # 尝试获取NASDAQ 100
        try:
            url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
            tables = pd.read_html(url)
            df = tables[4]
            nasdaq100 = df['Ticker'].tolist()
            symbols.extend(nasdaq100)
        except:
            # 备用列表
            nasdaq100_backup = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
                'COST', 'NFLX', 'ADBE', 'CSCO', 'PEP', 'TMUS', 'CMCSA', 'INTC',
                'AMD', 'QCOM', 'TXN', 'INTU', 'AMAT', 'ISRG', 'BKNG', 'ADP',
                'GILD', 'REGN', 'VRTX', 'LRCX', 'PANW', 'KLAC', 'SNPS', 'CDNS'
            ]
            symbols.extend(nasdaq100_backup)
        
        # 去重
        return list(set(symbols))
