"""
第三层：择时层 - 投票系统
三模型投票决策
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class VotingSystem:
    """投票系统"""

    def __init__(self):
        pass

    def vote(self, knn_signal: dict, svm_signal: dict, nlp_signal: dict) -> dict:
        """
        三模型投票

        Args:
            knn_signal: KNN信号
            svm_signal: SVM信号
            nlp_signal: NLP信号

        Returns:
            决策结果
        """
        # 统计看多票数
        bullish_votes = 0

        # KNN投票
        if knn_signal['signal'] in ['strong_bullish', 'bullish']:
            bullish_votes += 1

        # SVM投票
        if svm_signal['signal'] in ['strong_bullish', 'bullish']:
            bullish_votes += 1

        # NLP投票（反向操作）
        nlp_class = nlp_signal['sentiment_class']
        if nlp_class in ['extreme_bearish', 'bearish']:
            # 极度悲观时看多（反向）
            bullish_votes += 1
        elif nlp_class in ['extreme_bullish']:
            # 极度乐观时看空（反向）
            bullish_votes -= 1

        # 决策逻辑
        if bullish_votes >= 3:
            # 满仓信号
            action = 'full_position'
            target_position = 1.0
            reason = '三模型同时看多'
        elif bullish_votes == 2:
            # 半仓信号
            action = 'half_position'
            target_position = 0.5
            reason = '两模型看多'
        elif bullish_votes == 1:
            # 观望
            action = 'hold'
            target_position = 0.0
            reason = '信号不明确，观望'
        else:
            # 空仓
            action = 'empty_position'
            target_position = 0.0
            reason = '看空信号'

        # 特殊情况：极度恐慌时抄底
        if nlp_signal['sentiment_class'] == 'extreme_bearish' and \
           knn_signal['signal'] in ['bullish', 'strong_bullish']:
            action = 'full_position'
            target_position = 1.0
            reason = '极度恐慌抄底'

        # 特殊情况：极度乐观时逃顶
        if nlp_signal['sentiment_class'] == 'extreme_bullish' and \
           knn_signal['signal'] in ['bearish', 'strong_bearish']:
            action = 'empty_position'
            target_position = 0.0
            reason = '极度乐观逃顶'

        return {
            'action': action,
            'target_position': target_position,
            'reason': reason,
            'bullish_votes': bullish_votes
        }
