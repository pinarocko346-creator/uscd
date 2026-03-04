"""
第二层：轮动层 - 主程序
每周五计算，周一执行
"""
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer2_rotation.ic_calculator import ICCalculator
from layer2_rotation.random_forest_model import RandomForestModel
from utils import DataFetcher, layer2_logger
from config import LAYER2_INDEX, LAYER2_STOCK_COUNT, LAYER2_WEIGHT, TOTAL_CAPITAL


class Layer2Strategy:
    """第二层：轮动层策略"""

    def __init__(self):
        self.ic_calculator = ICCalculator()
        self.rf_model = RandomForestModel()
        self.data_fetcher = DataFetcher()
        self.logger = layer2_logger

        self.current_holdings = {}
        self.golden_factors = []

    def run(self, date: str = None):
        """运行策略"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"第二层：轮动层 - 开始运行 - {date}")
        self.logger.info(f"{'='*80}")

        try:
            # Step 1: 获取股票池
            self.logger.info("Step 1: 获取中证500成分股...")
            stock_codes = self.data_fetcher.get_index_stocks(LAYER2_INDEX, date)
            self.logger.info(f"  获取到 {len(stock_codes)} 只股票")

            # Step 2: 计算IC值，选出黄金因子
            self.logger.info("Step 2: 计算IC值，选出黄金因子...")
            golden_factors, ic_values = self.ic_calculator.select_golden_factors(stock_codes, date)
            self.golden_factors = golden_factors

            self.logger.info(f"  黄金因子: {golden_factors}")
            self.logger.info("  IC值排名:")
            for factor, ic in sorted(ic_values.items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
                self.logger.info(f"    {factor}: {ic:.4f}")

            # Step 3: 准备训练数据（简化处理）
            self.logger.info("Step 3: 准备训练数据...")
            # 实际应该获取历史数据并构建特征
            # 这里使用模拟数据
            X_train = pd.DataFrame(
                np.random.randn(100, len(golden_factors)),
                columns=golden_factors
            )
            y_train = pd.Series(np.random.randn(100) * 0.05)

            # Step 4: 训练随机森林
            self.logger.info("Step 4: 训练随机森林模型...")
            train_info = self.rf_model.train(X_train, y_train)
            self.logger.info(f"  训练集R²: {train_info['train_score']:.4f}")
            self.logger.info(f"  测试集R²: {train_info['test_score']:.4f}")
            if train_info['overfit']:
                self.logger.warning("  ⚠ 检测到过拟合")

            # Step 5: 预测并选股
            self.logger.info("Step 5: 预测未来收益并选股...")
            # 实际应该获取当前特征数据
            X_pred = pd.DataFrame(
                np.random.randn(len(stock_codes), len(golden_factors)),
                columns=golden_factors,
                index=stock_codes
            )
            predictions = self.rf_model.predict(X_pred)

            # 选出预测收益最高的股票
            top_stocks = predictions.nlargest(LAYER2_STOCK_COUNT)
            self.logger.info(f"  选中 {len(top_stocks)} 只股票")

            # Step 6: 生成持仓
            new_holdings = {code: 1.0/len(top_stocks) for code in top_stocks.index}

            # Step 7: 比较持仓变化
            old_codes = set(self.current_holdings.keys())
            new_codes = set(new_holdings.keys())

            trades = {
                'buy': list(new_codes - old_codes),
                'sell': list(old_codes - new_codes),
                'hold': list(old_codes & new_codes)
            }

            turnover_rate = len(trades['buy']) / LAYER2_STOCK_COUNT if LAYER2_STOCK_COUNT > 0 else 0

            self.logger.info(f"  买入: {len(trades['buy'])} 只")
            self.logger.info(f"  卖出: {len(trades['sell'])} 只")
            self.logger.info(f"  换手率: {turnover_rate*100:.1f}%")

            # 更新持仓
            self.current_holdings = new_holdings

            # 记录调仓
            self.logger.log_rebalance(
                layer="第二层：轮动层",
                date=date,
                holdings=self.current_holdings,
                trades=trades
            )

            # 资金分配
            layer2_capital = TOTAL_CAPITAL * LAYER2_WEIGHT
            self.logger.info(f"\n资金分配:")
            self.logger.info(f"  第二层总资金: {layer2_capital:,.0f} 元")
            self.logger.info(f"  持仓数量: {len(self.current_holdings)} 只")

            self.logger.info(f"\n{'='*80}")
            self.logger.info("第二层：轮动层 - 运行完成")
            self.logger.info(f"{'='*80}\n")

            return {
                'success': True,
                'holdings': self.current_holdings,
                'trades': trades,
                'golden_factors': golden_factors
            }

        except Exception as e:
            self.logger.error(f"运行失败: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """主函数"""
    strategy = Layer2Strategy()
    result = strategy.run()

    if result['success']:
        print("\n✓ 策略运行成功")
        print(f"持仓数量: {len(result['holdings'])} 只")
    else:
        print(f"\n✗ 策略运行失败: {result['error']}")


if __name__ == '__main__':
    main()
