"""
第三层：择时层 - 主程序
每日运行，三模型投票决策
"""
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer3_timing.knn_model import KNNModel
from layer3_timing.svm_model import SVMModel
from layer3_timing.nlp_model import NLPModel
from layer3_timing.voting_system import VotingSystem
from utils import DataFetcher, layer3_logger
from config import LAYER3_ETF, LAYER3_WEIGHT, TOTAL_CAPITAL


class Layer3Strategy:
    """第三层：择时层策略"""

    def __init__(self):
        self.knn_model = KNNModel()
        self.svm_model = SVMModel()
        self.nlp_model = NLPModel()
        self.voting_system = VotingSystem()
        self.data_fetcher = DataFetcher()
        self.logger = layer3_logger

        self.current_position = 0  # 0=空仓, 1=满仓

    def run(self, date: str = None):
        """运行策略"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"第三层：择时层 - 开始运行 - {date}")
        self.logger.info(f"{'='*80}")

        try:
            # Step 1: 获取指数数据
            self.logger.info("Step 1: 获取沪深300指数数据...")
            end_date = date
            start_date = pd.to_datetime(date) - pd.Timedelta(days=600)
            start_date = start_date.strftime('%Y-%m-%d')

            index_data = self.data_fetcher.get_index_data('000300', start_date, end_date)
            self.logger.info(f"  获取到 {len(index_data)} 天数据")

            # Step 2: KNN模型预测
            self.logger.info("\nStep 2: KNN模型预测...")
            knn_signal = self.knn_model.predict(index_data)
            self.logger.info(f"  KNN信号: {knn_signal['signal']}")
            self.logger.info(f"  上涨概率: {knn_signal['probability']*100:.1f}%")

            # Step 3: SVM模型预测
            self.logger.info("\nStep 3: SVM模型预测...")
            svm_signal = self.svm_model.predict(index_data)
            self.logger.info(f"  SVM信号: {svm_signal['signal']}")
            self.logger.info(f"  预测概率: {svm_signal['probability']*100:.1f}%")

            # Step 4: NLP情绪分析
            self.logger.info("\nStep 4: NLP情绪分析...")
            nlp_signal = self.nlp_model.analyze_sentiment(date)
            self.logger.info(f"  情绪得分: {nlp_signal['sentiment_score']:.2f}")
            self.logger.info(f"  情绪分类: {nlp_signal['sentiment_class']}")

            # Step 5: 三模型投票
            self.logger.info("\nStep 5: 三模型投票...")
            decision = self.voting_system.vote(knn_signal, svm_signal, nlp_signal)
            self.logger.info(f"  投票结果: {decision['action']}")
            self.logger.info(f"  目标仓位: {decision['target_position']*100:.0f}%")
            self.logger.info(f"  理由: {decision['reason']}")

            # Step 6: 执行决策
            old_position = self.current_position
            new_position = decision['target_position']

            action_desc = ""
            if new_position > old_position:
                action_desc = f"加仓 ({old_position*100:.0f}% → {new_position*100:.0f}%)"
            elif new_position < old_position:
                action_desc = f"减仓 ({old_position*100:.0f}% → {new_position*100:.0f}%)"
            else:
                action_desc = "保持"

            self.logger.info(f"\nStep 6: 执行决策 - {action_desc}")

            self.current_position = new_position

            # 资金分配
            layer3_capital = TOTAL_CAPITAL * LAYER3_WEIGHT
            position_capital = layer3_capital * new_position

            self.logger.info(f"\n资金分配:")
            self.logger.info(f"  第三层总资金: {layer3_capital:,.0f} 元")
            self.logger.info(f"  当前仓位: {new_position*100:.0f}%")
            self.logger.info(f"  持仓金额: {position_capital:,.0f} 元")
            self.logger.info(f"  现金: {(layer3_capital-position_capital):,.0f} 元")

            self.logger.info(f"\n{'='*80}")
            self.logger.info("第三层：择时层 - 运行完成")
            self.logger.info(f"{'='*80}\n")

            return {
                'success': True,
                'position': new_position,
                'decision': decision,
                'signals': {
                    'knn': knn_signal,
                    'svm': svm_signal,
                    'nlp': nlp_signal
                }
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
    strategy = Layer3Strategy()
    result = strategy.run()

    if result['success']:
        print("\n✓ 策略运行成功")
        print(f"当前仓位: {result['position']*100:.0f}%")
    else:
        print(f"\n✗ 策略运行失败: {result['error']}")


if __name__ == '__main__':
    main()
