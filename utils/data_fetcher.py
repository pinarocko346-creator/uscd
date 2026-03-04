"""
数据获取模块
支持多种数据源：Tushare、AKShare、本地数据
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional
import warnings
warnings.filterwarnings('ignore')


class DataFetcher:
    """数据获取器"""

    def __init__(self, data_source: str = "akshare", token: str = None):
        """
        初始化数据获取器

        Args:
            data_source: 数据源 ('tushare', 'akshare', 'local')
            token: Tushare token（如果使用tushare）
        """
        self.data_source = data_source
        self.token = token

        if data_source == "akshare":
            try:
                import akshare as ak
                self.ak = ak
                print(f"✓ AKShare初始化成功")
            except ImportError:
                print("✗ 未安装akshare，请运行: pip install akshare")
                self.data_source = "local"

    def get_index_stocks(self, index_code: str, date: str = None) -> List[str]:
        """
        获取指数成分股

        Args:
            index_code: 指数代码
                - '000300': 沪深300
                - '000905': 中证500
            date: 日期

        Returns:
            股票代码列表
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        try:
            if self.data_source == "akshare":
                return self._get_index_stocks_akshare(index_code)
            else:
                return self._get_index_stocks_sample(index_code)
        except Exception as e:
            print(f"获取指数成分股失败: {e}")
            return self._get_index_stocks_sample(index_code)

    def _get_index_stocks_akshare(self, index_code: str) -> List[str]:
        """AKShare获取指数成分股"""
        try:
            df = self.ak.index_stock_cons_csindex(symbol=index_code)
            if df is not None and len(df) > 0:
                return df['成分券代码'].tolist()
            return []
        except Exception as e:
            print(f"AKShare获取失败: {e}")
            return self._get_index_stocks_sample(index_code)

    def _get_index_stocks_sample(self, index_code: str) -> List[str]:
        """返回示例数据"""
        if index_code == '000300':  # 沪深300
            return [f"{i:06d}" for i in range(1, 301)]
        elif index_code == '000905':  # 中证500
            return [f"{i:06d}" for i in range(301, 801)]
        else:
            return []

    def get_stock_data(self, stock_code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with columns: ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        try:
            if self.data_source == "akshare":
                return self._get_stock_data_akshare(stock_code, start_date, end_date)
            else:
                return self._get_stock_data_sample(stock_code, start_date, end_date)
        except Exception as e:
            print(f"获取股票数据失败 {stock_code}: {e}")
            return None

    def _get_stock_data_akshare(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """AKShare获取股票数据"""
        df = self.ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            adjust="qfq"
        )

        if df is None or len(df) == 0:
            return None

        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume'
        })

        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        return df

    def _get_stock_data_sample(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成示例数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        dates = dates[dates.dayofweek < 5]

        np.random.seed(int(stock_code))
        base_price = 10 + np.random.rand() * 90
        prices = [base_price]

        for _ in range(len(dates) - 1):
            change = np.random.randn() * 0.02
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)

        prices = np.array(prices)

        data = {
            'open': prices * (1 + np.random.randn(len(prices)) * 0.01),
            'high': prices * (1 + abs(np.random.randn(len(prices))) * 0.02),
            'low': prices * (1 - abs(np.random.randn(len(prices))) * 0.02),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, len(prices))
        }

        df = pd.DataFrame(data, index=dates)
        return df

    def get_fundamentals(self, stock_codes: List[str]) -> pd.DataFrame:
        """
        获取财务数据

        Args:
            stock_codes: 股票代码列表

        Returns:
            DataFrame with columns: ['code', 'pe', 'pb', 'roe', 'gross_margin', 'market_cap']
        """
        data = []
        for code in stock_codes:
            np.random.seed(int(code))
            data.append({
                'code': code,
                'pe': 10 + np.random.rand() * 40,
                'pb': 1 + np.random.rand() * 5,
                'ps': 0.5 + np.random.rand() * 4.5,
                'roe': 0.05 + np.random.rand() * 0.20,
                'roa': 0.02 + np.random.rand() * 0.13,
                'gross_margin': 0.10 + np.random.rand() * 0.40,
                'net_margin': 0.05 + np.random.rand() * 0.25,
                'turnover': np.random.rand() * 0.10,
                'market_cap': 1e10 + np.random.rand() * 4e11,  # 100亿-5000亿
                'circ_market_cap': 1e10 + np.random.rand() * 4e11,
            })

        return pd.DataFrame(data)

    def get_index_data(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指数数据

        Args:
            index_code: 指数代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with columns: ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        try:
            if self.data_source == "akshare":
                return self._get_index_data_akshare(index_code, start_date, end_date)
            else:
                return self._get_index_data_sample(index_code, start_date, end_date)
        except Exception as e:
            print(f"获取指数数据失败 {index_code}: {e}")
            return self._get_index_data_sample(index_code, start_date, end_date)

    def _get_index_data_akshare(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """AKShare获取指数数据"""
        df = self.ak.stock_zh_index_daily(symbol=f"sh{index_code}")

        if df is None or len(df) == 0:
            return None

        df = df.rename(columns={
            'date': 'date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        })

        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        df = df.set_index('date')

        return df[['open', 'high', 'low', 'close', 'volume']]

    def _get_index_data_sample(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成示例指数数据"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        dates = dates[dates.dayofweek < 5]

        np.random.seed(42)
        base_price = 3000
        prices = [base_price]

        for _ in range(len(dates) - 1):
            change = np.random.randn() * 0.015
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)

        prices = np.array(prices)

        data = {
            'open': prices * (1 + np.random.randn(len(prices)) * 0.005),
            'high': prices * (1 + abs(np.random.randn(len(prices))) * 0.01),
            'low': prices * (1 - abs(np.random.randn(len(prices))) * 0.01),
            'close': prices,
            'volume': np.random.randint(1e9, 5e9, len(prices))
        }

        df = pd.DataFrame(data, index=dates)
        return df
