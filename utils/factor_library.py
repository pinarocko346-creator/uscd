"""
因子库
包含所有因子的计算函数
"""
import pandas as pd
import numpy as np
from scipy import stats


class FactorLibrary:
    """因子计算库"""

    @staticmethod
    def calculate_momentum(prices: pd.Series, period: int = 20) -> pd.Series:
        """
        计算动量因子

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            动量值（涨跌幅）
        """
        return prices.pct_change(period)

    @staticmethod
    def calculate_volatility(returns: pd.Series, period: int = 20) -> pd.Series:
        """
        计算波动率

        Args:
            returns: 收益率序列
            period: 周期

        Returns:
            波动率
        """
        return returns.rolling(window=period).std() * np.sqrt(252)

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        计算RSI指标

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            RSI值
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """
        计算MACD指标

        Args:
            prices: 价格序列
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            (MACD线, 信号线, 柱状图)
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    @staticmethod
    def standardize_factor(factor: pd.Series, method: str = 'zscore') -> pd.Series:
        """
        因子标准化

        Args:
            factor: 因子值
            method: 标准化方法 ('zscore', 'minmax', 'rank')

        Returns:
            标准化后的因子
        """
        if method == 'zscore':
            return (factor - factor.mean()) / factor.std()
        elif method == 'minmax':
            return (factor - factor.min()) / (factor.max() - factor.min())
        elif method == 'rank':
            return factor.rank() / len(factor)
        else:
            return factor

    @staticmethod
    def winsorize_factor(factor: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
        """
        因子去极值（Winsorize）

        Args:
            factor: 因子值
            lower: 下分位数
            upper: 上分位数

        Returns:
            去极值后的因子
        """
        lower_bound = factor.quantile(lower)
        upper_bound = factor.quantile(upper)

        return factor.clip(lower_bound, upper_bound)

    @staticmethod
    def calculate_ic(factor: pd.Series, returns: pd.Series) -> float:
        """
        计算因子IC值（信息系数）

        Args:
            factor: 因子值
            returns: 收益率

        Returns:
            IC值（皮尔逊相关系数）
        """
        # 对齐索引
        common_index = factor.index.intersection(returns.index)

        if len(common_index) < 10:
            return 0.0

        factor_aligned = factor.loc[common_index]
        returns_aligned = returns.loc[common_index]

        # 去除NaN
        mask = ~(factor_aligned.isna() | returns_aligned.isna())
        factor_clean = factor_aligned[mask]
        returns_clean = returns_aligned[mask]

        if len(factor_clean) < 10:
            return 0.0

        # 计算相关系数
        correlation, _ = stats.pearsonr(factor_clean, returns_clean)

        return correlation

    @staticmethod
    def neutralize_factor(factor: pd.Series, industry: pd.Series) -> pd.Series:
        """
        行业中性化

        Args:
            factor: 因子值
            industry: 行业分类

        Returns:
            中性化后的因子
        """
        # 简化版本：按行业减去均值
        result = factor.copy()

        for ind in industry.unique():
            mask = industry == ind
            if mask.sum() > 0:
                result[mask] = result[mask] - result[mask].mean()

        return result
