"""
性能指标计算模块
包含收益率、夏普比率、最大回撤、胜率等指标
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple


class PerformanceMetrics:
    """性能指标计算器"""

    @staticmethod
    def calculate_returns(prices: pd.Series) -> pd.Series:
        """
        计算收益率

        Args:
            prices: 价格序列

        Returns:
            收益率序列
        """
        return prices.pct_change()

    @staticmethod
    def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
        """
        计算累计收益率

        Args:
            returns: 收益率序列

        Returns:
            累计收益率序列
        """
        return (1 + returns).cumprod() - 1

    @staticmethod
    def calculate_annual_return(returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        计算年化收益率

        Args:
            returns: 收益率序列
            periods_per_year: 每年交易日数

        Returns:
            年化收益率
        """
        total_return = (1 + returns).prod() - 1
        n_periods = len(returns)
        years = n_periods / periods_per_year

        if years == 0:
            return 0.0

        annual_return = (1 + total_return) ** (1 / years) - 1
        return annual_return

    @staticmethod
    def calculate_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        计算年化波动率

        Args:
            returns: 收益率序列
            periods_per_year: 每年交易日数

        Returns:
            年化波动率
        """
        return returns.std() * np.sqrt(periods_per_year)

    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.03,
                               periods_per_year: int = 252) -> float:
        """
        计算夏普比率

        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率（年化）
            periods_per_year: 每年交易日数

        Returns:
            夏普比率
        """
        annual_return = PerformanceMetrics.calculate_annual_return(returns, periods_per_year)
        volatility = PerformanceMetrics.calculate_volatility(returns, periods_per_year)

        if volatility == 0:
            return 0.0

        sharpe = (annual_return - risk_free_rate) / volatility
        return sharpe

    @staticmethod
    def calculate_max_drawdown(prices: pd.Series) -> Tuple[float, pd.Timestamp, pd.Timestamp]:
        """
        计算最大回撤

        Args:
            prices: 价格序列

        Returns:
            (最大回撤, 开始日期, 结束日期)
        """
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max

        max_dd = drawdown.min()
        end_date = drawdown.idxmin()

        # 找到回撤开始日期
        start_date = cumulative[:end_date].idxmax()

        return max_dd, start_date, end_date

    @staticmethod
    def calculate_win_rate(returns: pd.Series) -> float:
        """
        计算胜率

        Args:
            returns: 收益率序列

        Returns:
            胜率（0-1之间）
        """
        if len(returns) == 0:
            return 0.0

        wins = (returns > 0).sum()
        total = len(returns)

        return wins / total

    @staticmethod
    def calculate_profit_loss_ratio(returns: pd.Series) -> float:
        """
        计算盈亏比

        Args:
            returns: 收益率序列

        Returns:
            盈亏比
        """
        wins = returns[returns > 0]
        losses = returns[returns < 0]

        if len(wins) == 0 or len(losses) == 0:
            return 0.0

        avg_win = wins.mean()
        avg_loss = abs(losses.mean())

        if avg_loss == 0:
            return 0.0

        return avg_win / avg_loss

    @staticmethod
    def calculate_calmar_ratio(returns: pd.Series, periods_per_year: int = 252) -> float:
        """
        计算卡玛比率

        Args:
            returns: 收益率序列
            periods_per_year: 每年交易日数

        Returns:
            卡玛比率
        """
        annual_return = PerformanceMetrics.calculate_annual_return(returns, periods_per_year)
        prices = (1 + returns).cumprod()
        max_dd, _, _ = PerformanceMetrics.calculate_max_drawdown(prices)

        if max_dd == 0:
            return 0.0

        return annual_return / abs(max_dd)

    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.03,
                                periods_per_year: int = 252) -> float:
        """
        计算索提诺比率

        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率（年化）
            periods_per_year: 每年交易日数

        Returns:
            索提诺比率
        """
        annual_return = PerformanceMetrics.calculate_annual_return(returns, periods_per_year)

        # 下行波动率（只考虑负收益）
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return 0.0

        downside_vol = downside_returns.std() * np.sqrt(periods_per_year)

        if downside_vol == 0:
            return 0.0

        sortino = (annual_return - risk_free_rate) / downside_vol
        return sortino

    @staticmethod
    def generate_report(returns: pd.Series, benchmark_returns: pd.Series = None) -> Dict:
        """
        生成完整的性能报告

        Args:
            returns: 策略收益率序列
            benchmark_returns: 基准收益率序列（可选）

        Returns:
            性能指标字典
        """
        prices = (1 + returns).cumprod()

        report = {
            '总收益率': (prices.iloc[-1] - 1) * 100,
            '年化收益率': PerformanceMetrics.calculate_annual_return(returns) * 100,
            '年化波动率': PerformanceMetrics.calculate_volatility(returns) * 100,
            '夏普比率': PerformanceMetrics.calculate_sharpe_ratio(returns),
            '最大回撤': PerformanceMetrics.calculate_max_drawdown(prices)[0] * 100,
            '胜率': PerformanceMetrics.calculate_win_rate(returns) * 100,
            '盈亏比': PerformanceMetrics.calculate_profit_loss_ratio(returns),
            '卡玛比率': PerformanceMetrics.calculate_calmar_ratio(returns),
            '索提诺比率': PerformanceMetrics.calculate_sortino_ratio(returns),
        }

        # 如果有基准，计算相对指标
        if benchmark_returns is not None:
            excess_returns = returns - benchmark_returns
            report['超额收益率'] = PerformanceMetrics.calculate_annual_return(excess_returns) * 100
            report['信息比率'] = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)

        return report

    @staticmethod
    def print_report(report: Dict):
        """
        打印性能报告

        Args:
            report: 性能指标字典
        """
        print("\n" + "=" * 60)
        print("性能报告")
        print("=" * 60)

        for key, value in report.items():
            if '率' in key or '比' in key:
                if '比率' in key or '比' == key[-1]:
                    print(f"{key:15s}: {value:8.2f}")
                else:
                    print(f"{key:15s}: {value:8.2f}%")
            else:
                print(f"{key:15s}: {value:8.2f}")

        print("=" * 60)
