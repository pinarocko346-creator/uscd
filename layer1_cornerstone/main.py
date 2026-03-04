"""
第一层：基石层 - 主程序
每月第一个交易日执行，选出20只股票等权重配置
"""
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer1_cornerstone.factor_calculator import FactorCalculator
from layer1_cornerstone.stock_selector import StockSelector
from layer1_cornerstone.risk_manager import RiskManager
from utils import DataFetcher, layer1_logger
from config import LAYER1_INDEX, LAYER1_WEIGHT, TOTAL_CAPITAL


class Layer1Strategy:
    """第一层：基石层策略"""

    def __init__(self):
        self.factor_calculator = FactorCalculator()
        self.stock_selector = StockSelector()
        self.risk_manager = RiskManager()
        self.data_fetcher = DataFetcher()
        self.logger = layer1_logger

        # 状态变量
        self.current_holdings = {}
        self.entry_prices = {}
        self.portfolio_values = pd.Series()

    def run(self, date: str = None):
        """
        运行策略

        Args:
            date: 运行日期（默认为今天）
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"第一层：基石层 - 开始运行 - {date}")
        self.logger.info(f"{'='*80}")

        try:
            # Step 1: 获取股票池
            self.logger.info("Step 1: 获取沪深300成分股...")
            stock_codes = self.data_fetcher.get_index_stocks(LAYER1_INDEX, date)
            self.logger.info(f"  获取到 {len(stock_codes)} 只股票")

            # Step 2: 计算因子
            self.logger.info("Step 2: 计算因子...")
            factors_df = self.factor_calculator.calculate_all_factors(stock_codes, date)
            self.logger.info(f"  计算完成，共 {len(factors_df)} 只股票")

            # Step 3: 因子标准化
            self.logger.info("Step 3: 因子标准化...")
            factors_df = self.factor_calculator.standardize_factors(factors_df)

            # Step 4: 计算综合得分
            self.logger.info("Step 4: 计算综合得分...")
            factors_df = self.factor_calculator.calculate_composite_score(factors_df)

            # Step 5: 筛选股票
            self.logger.info("Step 5: 筛选股票...")
            filtered_df = self.stock_selector.filter_stocks(factors_df)
            self.logger.info(f"  筛选后剩余 {len(filtered_df)} 只股票")

            # Step 6: 选出Top20
            self.logger.info("Step 6: 选出前20只股票...")
            selected_df = self.stock_selector.select_top_stocks(filtered_df)
            self.logger.info(f"  选中 {len(selected_df)} 只股票")

            # 打印选中的股票
            for i, row in selected_df.head(10).iterrows():
                self.logger.info(f"  {i+1}. {row['code']} - 得分: {row['composite_score']:.4f}")
            if len(selected_df) > 10:
                self.logger.info("  ...")

            # Step 7: 生成持仓
            self.logger.info("Step 7: 生成持仓...")
            new_holdings = self.stock_selector.generate_holdings(selected_df)

            # Step 8: 比较持仓变化
            self.logger.info("Step 8: 生成交易指令...")
            trades = self.stock_selector.compare_holdings(self.current_holdings, new_holdings)
            self.logger.info(f"  买入: {len(trades['buy'])} 只")
            self.logger.info(f"  卖出: {len(trades['sell'])} 只")
            self.logger.info(f"  保持: {len(trades['hold'])} 只")

            # Step 9: 风险检查
            self.logger.info("Step 9: 风险检查...")
            risk_checks = self._perform_risk_checks(date)

            # Step 10: 应用风险控制
            if any([v.get('triggered') for v in risk_checks.values() if isinstance(v, dict)]):
                self.logger.warning("  检测到风险，应用风险控制措施...")
                new_holdings = self.risk_manager.apply_risk_controls(new_holdings, risk_checks)

            # Step 11: 更新持仓
            self.current_holdings = new_holdings

            # 记录调仓
            self.logger.log_rebalance(
                layer="第一层：基石层",
                date=date,
                holdings=self.current_holdings,
                trades=trades
            )

            # 计算资金分配
            layer1_capital = TOTAL_CAPITAL * LAYER1_WEIGHT
            self.logger.info(f"\n资金分配:")
            self.logger.info(f"  第一层总资金: {layer1_capital:,.0f} 元")
            self.logger.info(f"  持仓数量: {len(self.current_holdings)} 只")
            if len(self.current_holdings) > 0:
                per_stock = layer1_capital / len(self.current_holdings)
                self.logger.info(f"  每只股票: {per_stock:,.0f} 元 ({100/len(self.current_holdings):.2f}%)")

            self.logger.info(f"\n{'='*80}")
            self.logger.info("第一层：基石层 - 运行完成")
            self.logger.info(f"{'='*80}\n")

            return {
                'success': True,
                'holdings': self.current_holdings,
                'trades': trades,
                'selected_stocks': selected_df
            }

        except Exception as e:
            self.logger.error(f"运行失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

    def _perform_risk_checks(self, date: str) -> dict:
        """执行风险检查"""
        risk_checks = {}

        # 单股止损检查（需要价格数据）
        # risk_checks['stop_loss_stocks'] = self.risk_manager.check_single_stock_stop_loss(...)

        # 组合回撤检查
        if len(self.portfolio_values) > 0:
            risk_checks['portfolio_drawdown'] = self.risk_manager.check_portfolio_drawdown(
                self.portfolio_values
            )

        # 系统性风险检查（需要指数数据）
        # risk_checks['systemic_risk'] = self.risk_manager.check_systemic_risk(...)

        return risk_checks

    def get_holdings(self) -> dict:
        """获取当前持仓"""
        return self.current_holdings


def main():
    """主函数"""
    strategy = Layer1Strategy()
    result = strategy.run()

    if result['success']:
        print("\n✓ 策略运行成功")
        print(f"持仓数量: {len(result['holdings'])} 只")
    else:
        print(f"\n✗ 策略运行失败: {result['error']}")


if __name__ == '__main__':
    main()
