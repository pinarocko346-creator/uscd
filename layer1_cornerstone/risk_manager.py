"""
第一层：基石层 - 风险管理器
实现单股止损、组合回撤控制等风险管理功能
"""
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    LAYER1_SINGLE_STOCK_STOP_LOSS,
    LAYER1_PORTFOLIO_DRAWDOWN_THRESHOLD,
    LAYER1_UNDERPERFORM_MONTHS,
    LAYER1_SYSTEMIC_RISK_THRESHOLD,
    LAYER1_SYSTEMIC_RISK_POSITION_CUT,
    LAYER1_FACTOR_IC_THRESHOLD,
    LAYER1_FACTOR_IC_CHECK_MONTHS
)
from utils import FactorLibrary


class RiskManager:
    """风险管理器"""

    def __init__(self):
        self.factor_lib = FactorLibrary()

    def check_single_stock_stop_loss(self, holdings: dict, current_prices: dict,
                                     entry_prices: dict) -> list:
        """
        检查单股止损

        Args:
            holdings: 当前持仓 {股票代码: 权重}
            current_prices: 当前价格 {股票代码: 价格}
            entry_prices: 买入价格 {股票代码: 价格}

        Returns:
            需要止损的股票列表
        """
        stop_loss_stocks = []

        for code in holdings.keys():
            if code not in current_prices or code not in entry_prices:
                continue

            current_price = current_prices[code]
            entry_price = entry_prices[code]

            # 计算收益率
            return_rate = (current_price - entry_price) / entry_price

            # 检查是否触发止损
            if return_rate <= LAYER1_SINGLE_STOCK_STOP_LOSS:
                stop_loss_stocks.append({
                    'code': code,
                    'return': return_rate,
                    'reason': f'单股止损 ({return_rate*100:.2f}%)'
                })

        return stop_loss_stocks

    def check_portfolio_drawdown(self, portfolio_values: pd.Series) -> dict:
        """
        检查组合回撤

        Args:
            portfolio_values: 组合净值序列

        Returns:
            回撤信息字典
        """
        if len(portfolio_values) == 0:
            return {'drawdown': 0, 'triggered': False}

        # 计算回撤
        cummax = portfolio_values.expanding().max()
        drawdown = (portfolio_values - cummax) / cummax

        current_drawdown = drawdown.iloc[-1]

        return {
            'drawdown': current_drawdown,
            'triggered': current_drawdown <= LAYER1_PORTFOLIO_DRAWDOWN_THRESHOLD,
            'threshold': LAYER1_PORTFOLIO_DRAWDOWN_THRESHOLD
        }

    def check_underperformance(self, strategy_returns: pd.Series,
                               benchmark_returns: pd.Series) -> dict:
        """
        检查连续跑输基准

        Args:
            strategy_returns: 策略收益率（月度）
            benchmark_returns: 基准收益率（月度）

        Returns:
            跑输信息字典
        """
        if len(strategy_returns) < LAYER1_UNDERPERFORM_MONTHS:
            return {'triggered': False, 'months': 0}

        # 计算超额收益
        excess_returns = strategy_returns - benchmark_returns

        # 检查最近N个月
        recent_excess = excess_returns.tail(LAYER1_UNDERPERFORM_MONTHS)

        # 是否全部为负
        all_negative = (recent_excess < 0).all()

        return {
            'triggered': all_negative,
            'months': LAYER1_UNDERPERFORM_MONTHS if all_negative else 0,
            'avg_underperform': recent_excess.mean() if all_negative else 0
        }

    def check_systemic_risk(self, index_returns: pd.Series) -> dict:
        """
        检查系统性风险

        Args:
            index_returns: 指数收益率（月度）

        Returns:
            系统性风险信息
        """
        if len(index_returns) == 0:
            return {'triggered': False, 'return': 0}

        # 最近一个月收益
        last_month_return = index_returns.iloc[-1]

        triggered = last_month_return <= LAYER1_SYSTEMIC_RISK_THRESHOLD

        return {
            'triggered': triggered,
            'return': last_month_return,
            'threshold': LAYER1_SYSTEMIC_RISK_THRESHOLD,
            'action': 'reduce_position' if triggered else 'none',
            'target_position': LAYER1_SYSTEMIC_RISK_POSITION_CUT if triggered else 1.0
        }

    def check_factor_effectiveness(self, factor_ic_history: pd.DataFrame) -> dict:
        """
        检查因子有效性

        Args:
            factor_ic_history: 因子IC历史 DataFrame(columns=['date', 'factor', 'ic'])

        Returns:
            因子有效性信息
        """
        if len(factor_ic_history) < LAYER1_FACTOR_IC_CHECK_MONTHS:
            return {'triggered': False, 'invalid_factors': []}

        # 获取最近N个月的IC
        recent_ic = factor_ic_history.tail(LAYER1_FACTOR_IC_CHECK_MONTHS)

        # 按因子分组，检查IC是否持续低于阈值
        invalid_factors = []

        for factor in recent_ic['factor'].unique():
            factor_ic = recent_ic[recent_ic['factor'] == factor]['ic']

            # 如果所有IC都低于阈值
            if (factor_ic < LAYER1_FACTOR_IC_THRESHOLD).all():
                invalid_factors.append({
                    'factor': factor,
                    'avg_ic': factor_ic.mean()
                })

        return {
            'triggered': len(invalid_factors) > 0,
            'invalid_factors': invalid_factors
        }

    def apply_risk_controls(self, holdings: dict, risk_checks: dict) -> dict:
        """
        应用风险控制措施

        Args:
            holdings: 当前持仓
            risk_checks: 风险检查结果

        Returns:
            调整后的持仓
        """
        adjusted_holdings = holdings.copy()

        # 单股止损
        if risk_checks.get('stop_loss_stocks'):
            for stock_info in risk_checks['stop_loss_stocks']:
                code = stock_info['code']
                if code in adjusted_holdings:
                    del adjusted_holdings[code]

        # 组合回撤控制
        if risk_checks.get('portfolio_drawdown', {}).get('triggered'):
            # 减仓50%
            for code in adjusted_holdings:
                adjusted_holdings[code] *= 0.5

        # 系统性风险应对
        if risk_checks.get('systemic_risk', {}).get('triggered'):
            target_position = risk_checks['systemic_risk']['target_position']
            for code in adjusted_holdings:
                adjusted_holdings[code] *= target_position

        return adjusted_holdings
