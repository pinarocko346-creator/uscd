"""
第三层：择时层 - KNN模型
基于历史相似度预测
"""
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import FactorLibrary
from config import LAYER3_KNN_PARAMS, LAYER3_KNN_FEATURES, LAYER3_KNN_TRAIN_PERIOD


class KNNModel:
    """KNN模型"""

    def __init__(self):
        self.model = None
        self.factor_lib = FactorLibrary()

    def extract_features(self, index_data: pd.DataFrame) -> pd.DataFrame:
        """
        提取特征

        Args:
            index_data: 指数数据

        Returns:
            特征DataFrame
        """
        features = pd.DataFrame(index=index_data.index)

        # 计算各种收益率
        features['return_1d'] = index_data['close'].pct_change(1)
        features['return_2d'] = index_data['close'].pct_change(2)
        features['return_3d'] = index_data['close'].pct_change(3)
        features['return_5d'] = index_data['close'].pct_change(5)
        features['return_10d'] = index_data['close'].pct_change(10)

        # 成交量比率
        features['volume_ratio'] = index_data['volume'] / index_data['volume'].rolling(10).mean()

        # RSI
        features['rsi_14'] = self.factor_lib.calculate_rsi(index_data['close'], 14)

        # MACD
        _, _, macd_hist = self.factor_lib.calculate_macd(index_data['close'])
        features['macd_hist'] = macd_hist

        # 均线偏离度
        ma_20 = index_data['close'].rolling(20).mean()
        features['ma_deviation_20'] = (index_data['close'] - ma_20) / ma_20

        # 填充缺失值
        features = features.fillna(0)

        return features

    def train(self, index_data: pd.DataFrame):
        """
        训练模型

        Args:
            index_data: 指数数据
        """
        # 提取特征
        features = self.extract_features(index_data)

        # 计算标签（次日涨跌）
        labels = (index_data['close'].shift(-1) > index_data['close']).astype(int)

        # 去除缺失值
        valid_idx = ~(features.isna().any(axis=1) | labels.isna())
        X = features[valid_idx]
        y = labels[valid_idx]

        # 只使用最近的数据训练
        if len(X) > LAYER3_KNN_TRAIN_PERIOD:
            X = X.tail(LAYER3_KNN_TRAIN_PERIOD)
            y = y.tail(LAYER3_KNN_TRAIN_PERIOD)

        # 训练模型
        self.model = KNeighborsClassifier(**LAYER3_KNN_PARAMS)
        self.model.fit(X, y)

    def predict(self, index_data: pd.DataFrame) -> dict:
        """
        预测

        Args:
            index_data: 指数数据

        Returns:
            预测信号
        """
        # 训练模型（使用历史数据）
        self.train(index_data)

        # 提取最新特征
        features = self.extract_features(index_data)
        latest_features = features.iloc[[-1]]

        # 预测
        prediction = self.model.predict(latest_features)[0]
        probability = self.model.predict_proba(latest_features)[0][1]  # 上涨概率

        # 生成信号
        if probability >= 0.8:
            signal = 'strong_bullish'
        elif probability >= 0.6:
            signal = 'bullish'
        elif probability >= 0.4:
            signal = 'neutral'
        elif probability >= 0.2:
            signal = 'bearish'
        else:
            signal = 'strong_bearish'

        return {
            'signal': signal,
            'prediction': prediction,
            'probability': probability
        }
