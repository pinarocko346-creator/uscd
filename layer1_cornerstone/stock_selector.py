"""
第一层：基石层 - 选股器
根据因子得分选出前20只股票
"""
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    LAYER1_STOCK_COUNT,
    LAYER1_FACTOR_FILTERS
)


class StockSelector:
    """选股器"""

    def __init__(self):
        pass

    def filter_stocks(self, factors_df: pd.DataFrame) -> pd.DataFrame:
        """
        根据硬性条件筛选股票

        Args:
            factors_df: 因子DataFrame

        Returns:
            筛选后的DataFrame
        """
        result_df = factors_df.copy()

        # 应用筛选条件
        for factor_name, thresholds in LAYER1_FACTOR_FILTERS.items():
            if factor_name not in result_df.columns:
                continue

            min_val = thresholds.get('min')
            max_val = thresholds.get('max')

            if min_val is not None:
                result_df = result_df[result_df[factor_name] >= min_val]

            if max_val is not None:
                result_df = result_df[result_df[factor_name] <= max_val]

        return result_df

    def select_top_stocks(self, factors_df: pd.DataFrame, n: int = None) -> pd.DataFrame:
        """
        选出得分最高的N只股票

        Args:
            factors_df: 因子DataFrame（包含composite_score）
            n: 选股数量

        Returns:
            选中的股票DataFrame
        """
        n = n or LAYER1_STOCK_COUNT

        # 按综合得分排序
        sorted_df = factors_df.sort_values('composite_score', ascending=False)

        # 选出前N只
        selected_df = sorted_df.head(n)

        return selected_df

    def generate_holdings(self, selected_df: pd.DataFrame) -> dict:
        """
        生成持仓字典（等权重）

        Args:
            selected_df: 选中的股票DataFrame

        Returns:
            持仓字典 {股票代码: 权重}
        """
        n_stocks = len(selected_df)
        if n_stocks == 0:
            return {}

        weight = 1.0 / n_stocks

        holdings = {}
        for code in selected_df['code']:
            holdings[code] = weight

        return holdings

    def compare_holdings(self, old_holdings: dict, new_holdings: dict) -> dict:
        """
        比较新旧持仓，生成交易指令

        Args:
            old_holdings: 旧持仓
            new_holdings: 新持仓

        Returns:
            交易指令 {'buy': [...], 'sell': [...], 'hold': [...]}
        """
        old_codes = set(old_holdings.keys())
        new_codes = set(new_holdings.keys())

        trades = {
            'buy': list(new_codes - old_codes),
            'sell': list(old_codes - new_codes),
            'hold': list(old_codes & new_codes)
        }

        return trades
