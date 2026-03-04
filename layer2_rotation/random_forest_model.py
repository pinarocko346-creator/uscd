"""
第二层：轮动层 - 随机森林模型
使用随机森林预测未来5日收益
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    LAYER2_RF_PARAMS,
    LAYER2_TRAIN_PERIOD,
    LAYER2_PREDICT_PERIOD,
    LAYER2_OVERFIT_R2_THRESHOLD
)


class RandomForestModel:
    """随机森林模型"""

    def __init__(self):
        self.model = None
        self.feature_importance = None

    def train(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """
        训练模型

        Args:
            X: 特征数据
            y: 目标变量（未来收益）

        Returns:
            训练信息
        """
        # 分割训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 创建模型
        self.model = RandomForestRegressor(**LAYER2_RF_PARAMS)

        # 训练
        self.model.fit(X_train, y_train)

        # 评估
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        # 特征重要性
        self.feature_importance = pd.Series(
            self.model.feature_importances_,
            index=X.columns
        ).sort_values(ascending=False)

        # 过拟合检测
        overfit = train_score > LAYER2_OVERFIT_R2_THRESHOLD or \
                  (train_score - test_score) > 0.3

        return {
            'train_score': train_score,
            'test_score': test_score,
            'overfit': overfit,
            'feature_importance': self.feature_importance
        }

    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        预测

        Args:
            X: 特征数据

        Returns:
            预测值
        """
        if self.model is None:
            raise ValueError("模型未训练")

        predictions = self.model.predict(X)
        return pd.Series(predictions, index=X.index)

    def get_feature_importance(self) -> pd.Series:
        """获取特征重要性"""
        return self.feature_importance
