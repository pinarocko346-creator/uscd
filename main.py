"""
三层量化系统 - 主程序入口
协调三层策略运行
"""
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from layer1_cornerstone import Layer1Strategy
from layer2_rotation import Layer2Strategy
from layer3_timing import Layer3Strategy
from utils import system_logger, PerformanceMetrics
from config import TOTAL_CAPITAL, LAYER1_WEIGHT, LAYER2_WEIGHT, LAYER3_WEIGHT


class ThreeLayerSystem:
    """三层量化系统"""

    def __init__(self):
        self.layer1 = Layer1Strategy()
        self.layer2 = Layer2Strategy()
        self.layer3 = Layer3Strategy()
        self.logger = system_logger

    def run(self, date: str = None):
        """
        运行系统

        Args:
            date: 运行日期
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        self.logger.info("\n" + "="*80)
        self.logger.info("三层量化系统 - 开始运行")
        self.logger.info(f"日期: {date}")
        self.logger.info("="*80)

        results = {}

        # 运行第一层：基石层（月频）
        self.logger.info("\n>>> 运行第一层：基石层")
        try:
            result1 = self.layer1.run(date)
            results['layer1'] = result1
            if result1['success']:
                self.logger.info("✓ 第一层运行成功")
            else:
                self.logger.error(f"✗ 第一层运行失败: {result1.get('error')}")
        except Exception as e:
            self.logger.error(f"✗ 第一层运行异常: {str(e)}")
            results['layer1'] = {'success': False, 'error': str(e)}

        # 运行第二层：轮动层（周频）
        self.logger.info("\n>>> 运行第二层：轮动层")
        try:
            result2 = self.layer2.run(date)
            results['layer2'] = result2
            if result2['success']:
                self.logger.info("✓ 第二层运行成功")
            else:
                self.logger.error(f"✗ 第二层运行失败: {result2.get('error')}")
        except Exception as e:
            self.logger.error(f"✗ 第二层运行异常: {str(e)}")
            results['layer2'] = {'success': False, 'error': str(e)}

        # 运行第三层：择时层（日频）
        self.logger.info("\n>>> 运行第三层：择时层")
        try:
            result3 = self.layer3.run(date)
            results['layer3'] = result3
            if result3['success']:
                self.logger.info("✓ 第三层运行成功")
            else:
                self.logger.error(f"✗ 第三层运行失败: {result3.get('error')}")
        except Exception as e:
            self.logger.error(f"✗ 第三层运行异常: {str(e)}")
            results['layer3'] = {'success': False, 'error': str(e)}

        # 汇总报告
        self._generate_summary(date, results)

        return results

    def _generate_summary(self, date: str, results: dict):
        """生成汇总报告"""
        self.logger.info("\n" + "="*80)
        self.logger.info("系统运行汇总")
        self.logger.info("="*80)

        # 资金分配
        self.logger.info("\n资金分配:")
        self.logger.info(f"  总资金: {TOTAL_CAPITAL:,.0f} 元")
        self.logger.info(f"  第一层（基石层）: {TOTAL_CAPITAL*LAYER1_WEIGHT:,.0f} 元 ({LAYER1_WEIGHT*100:.0f}%)")
        self.logger.info(f"  第二层（轮动层）: {TOTAL_CAPITAL*LAYER2_WEIGHT:,.0f} 元 ({LAYER2_WEIGHT*100:.0f}%)")
        self.logger.info(f"  第三层（择时层）: {TOTAL_CAPITAL*LAYER3_WEIGHT:,.0f} 元 ({LAYER3_WEIGHT*100:.0f}%)")

        # 持仓统计
        self.logger.info("\n持仓统计:")

        if results.get('layer1', {}).get('success'):
            layer1_holdings = results['layer1'].get('holdings', {})
            self.logger.info(f"  第一层: {len(layer1_holdings)} 只股票")

        if results.get('layer2', {}).get('success'):
            layer2_holdings = results['layer2'].get('holdings', {})
            self.logger.info(f"  第二层: {len(layer2_holdings)} 只股票")

        if results.get('layer3', {}).get('success'):
            layer3_position = results['layer3'].get('position', 0)
            self.logger.info(f"  第三层: {layer3_position*100:.0f}% 仓位")

        # 运行状态
        self.logger.info("\n运行状态:")
        success_count = sum(1 for r in results.values() if r.get('success'))
        self.logger.info(f"  成功: {success_count}/3 层")

        self.logger.info("\n" + "="*80)
        self.logger.info("系统运行完成")
        self.logger.info("="*80 + "\n")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("三层量化交易系统")
    print("="*80)
    print("\n系统说明:")
    print("  第一层（基石层）: 多因子回归，月频调仓，50%仓位")
    print("  第二层（轮动层）: 随机森林，周频调仓，30%仓位")
    print("  第三层（择时层）: KNN+SVM+NLP，日频调仓，20%仓位")
    print("\n" + "="*80 + "\n")

    # 创建系统实例
    system = ThreeLayerSystem()

    # 运行系统
    results = system.run()

    # 打印结果
    print("\n" + "="*80)
    print("运行结果")
    print("="*80)

    for layer_name, result in results.items():
        status = "✓ 成功" if result.get('success') else "✗ 失败"
        print(f"{layer_name}: {status}")

    print("="*80 + "\n")


if __name__ == '__main__':
    main()
