"""
第二层：轮动层 - IC计算器
计算各因子的IC值，选出黄金因子
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import FactorLibrary, DataFetcher
from config import (
    LAYER2_CANDIDATE_FACTORS,
    LAYER2_GOLDEN_FACTOR_COUNT,
    LAYER2_IC_PERIOD,
    LAYER2_IC_MIN_THRESHOLD
)


class ICCalculator:
    """IC值计算器"""

    def __init__(self):
        self.factor_lib = FactorLibrary()
        self.data_fetcher = DataFetcher()

    def calculate_factor_ic(self, stock_codes: list, factor_name: str,
                           start_date: str, end_date: str) -> float:
        """
        计算单个因子的IC值

        Args:
            stock_codes: 股票代码列表
            factor_name: 因子名称
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            IC值
        """
        # 获取因子数据和收益数据
        # 这里简化处理，实际应该获取真实数据
        factor_values = []
        returns = []

        for code in stock_codes:
            try:
                # 获取价格数据
                price_data = self.data_fetcher.get_stock_data(code, start_date, end_date)
                if price_data is None or len(price_data) < 10:
                    continue

                # 计算因子值（简化）
                if 'Momentum' in factor_name:
                    period = int(factor_name.split('_')[1]) if '_' in factor_name else 20
                    factor_val = self.factor_lib.calculate_momentum(price_data['close'], period).iloc[-1]
                else:
                    # 其他因子从财务数据获取
                    financial_data = self.data_fetcher.get_fundamentals([code])
                    factor_val = financial_data[factor_name.lower()].iloc[0] if factor_name.lower() in financial_data.columns else 0

                # 计算未来收益
                future_return = price_data['close'].pct_change(5).iloc[-1]

                if not pd.isna(factor_val) and not pd.isna(future_return):
                    factor_values.append(factor_val)
                    returns.append(future_return)

            except:
                continue

        # 计算IC（相关系数）
        if len(factor_values) < 10:
            return 0.0

        ic = self.factor_lib.calculate_ic(
            pd.Series(factor_values),
            pd.Series(returns)
        )

        return ic

    def select_golden_factors(self, stock_codes: list, date: str) -> list:
        """
        选出黄金因子

        Args:
            stock_codes: 股票代码列表
            date: 日期

        Returns:
            黄金因子列表
        """
        # 计算日期范围
        end_date = date
        start_date = pd.to_datetime(date) - pd.Timedelta(days=LAYER2_IC_PERIOD)
        start_date = start_date.strftime('%Y-%m-%d')

        # 计算各因子IC值
        ic_values = {}

        for factor_name in LAYER2_CANDIDATE_FACTORS:
            ic = self.calculate_factor_ic(stock_codes, factor_name, start_date, end_date)
            ic_values[factor_name] = ic

        # 排序并选出Top N
        sorted_factors = sorted(ic_values.items(), key=lambda x: abs(x[1]), reverse=True)

        # 过滤掉IC值过低的因子
        golden_factors = [
            factor for factor, ic in sorted_factors[:LAYER2_GOLDEN_FACTOR_COUNT]
            if abs(ic) >= LAYER2_IC_MIN_THRESHOLD
        ]

        return golden_factors, ic_values
