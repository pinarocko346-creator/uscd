"""
第一层：基石层 - 因子计算器
计算PE、PB、ROE、毛利率、动量等因子
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import FactorLibrary, DataFetcher
from config import (
    LAYER1_FACTOR_WEIGHTS,
    LAYER1_FACTOR_DIRECTION,
    LAYER1_MOMENTUM_PERIOD,
    LAYER1_STANDARDIZE_METHOD,
    LAYER1_WINSORIZE_LOWER,
    LAYER1_WINSORIZE_UPPER
)


class FactorCalculator:
    """因子计算器"""

    def __init__(self):
        self.factor_lib = FactorLibrary()
        self.data_fetcher = DataFetcher()

    def calculate_all_factors(self, stock_codes: list, date: str) -> pd.DataFrame:
        """
        计算所有因子

        Args:
            stock_codes: 股票代码列表
            date: 计算日期

        Returns:
            DataFrame，包含所有因子
        """
        # 获取财务数据
        financial_data = self.data_fetcher.get_fundamentals(stock_codes)

        # 获取价格数据（用于计算动量）
        end_date = date
        start_date = pd.to_datetime(date) - pd.Timedelta(days=60)
        start_date = start_date.strftime('%Y-%m-%d')

        # 计算动量因子
        momentum_data = []
        for code in stock_codes:
            try:
                price_data = self.data_fetcher.get_stock_data(code, start_date, end_date)
                if price_data is not None and len(price_data) >= LAYER1_MOMENTUM_PERIOD:
                    momentum = self.factor_lib.calculate_momentum(
                        price_data['close'],
                        LAYER1_MOMENTUM_PERIOD
                    )
                    momentum_data.append({
                        'code': code,
                        'Momentum': momentum.iloc[-1] if not pd.isna(momentum.iloc[-1]) else 0
                    })
                else:
                    momentum_data.append({'code': code, 'Momentum': 0})
            except:
                momentum_data.append({'code': code, 'Momentum': 0})

        momentum_df = pd.DataFrame(momentum_data)

        # 合并数据
        factors_df = financial_data.merge(momentum_df, on='code', how='left')

        # 重命名列
        factors_df = factors_df.rename(columns={
            'pe': 'PE',
            'pb': 'PB',
            'roe': 'ROE',
            'gross_margin': 'GrossMargin',
            'market_cap': 'MarketCap'
        })

        return factors_df

    def standardize_factors(self, factors_df: pd.DataFrame) -> pd.DataFrame:
        """
        因子标准化

        Args:
            factors_df: 因子DataFrame

        Returns:
            标准化后的DataFrame
        """
        result_df = factors_df.copy()

        for factor_name in LAYER1_FACTOR_WEIGHTS.keys():
            if factor_name not in result_df.columns:
                continue

            # 去极值
            result_df[factor_name] = self.factor_lib.winsorize_factor(
                result_df[factor_name],
                LAYER1_WINSORIZE_LOWER,
                LAYER1_WINSORIZE_UPPER
            )

            # 标准化
            result_df[f'{factor_name}_std'] = self.factor_lib.standardize_factor(
                result_df[factor_name],
                LAYER1_STANDARDIZE_METHOD
            )

            # 调整方向（价值因子取负）
            direction = LAYER1_FACTOR_DIRECTION.get(factor_name, 1)
            result_df[f'{factor_name}_std'] *= direction

        return result_df

    def calculate_composite_score(self, factors_df: pd.DataFrame) -> pd.DataFrame:
        """
        计算综合得分

        Args:
            factors_df: 标准化后的因子DataFrame

        Returns:
            包含综合得分的DataFrame
        """
        result_df = factors_df.copy()

        # 计算加权得分
        result_df['composite_score'] = 0

        for factor_name, weight in LAYER1_FACTOR_WEIGHTS.items():
            std_col = f'{factor_name}_std'
            if std_col in result_df.columns:
                result_df['composite_score'] += result_df[std_col] * weight

        return result_df
