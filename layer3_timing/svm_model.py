"""
第三层：择时层 - SVM模型
"""
import pandas as pd
import numpy as np
from sklearn.svm import SVC
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import FactorLibrary
from config import LAYER3_SVM_PARAMS, LAYER3_SVM_TRAIN_PERIOD


class SVMModel:
    """SVM模型"""

    def __init__(self):
        self.model = None
        self.factor_lib = FactorLibrary()

    def extract_features(self, index_data: pd.DataFrame) -> pd.DataFrame:
        """提取特征（与KNN类似，但增加额外特征）"""
        features = pd.DataFrame(index=index_data.index)

        # 基础特征
        features['return_1d'] = index_data['close'].pct_change(1)
        features['return_5d'] = index_data['close'].pct_change(5)
        features['volume_ratio'] = index_data['volume'] / index_data['volume'].rolling(10).mean()
        features['rsi_14'] = self.factor_lib.calculate_rsi(index_data['close'], 14)

        _, _, macd_hist = self.factor_lib.calculate_macd(index_data['close'])
        features['macd_hist'] = macd_hist

        # 额外特征
        features['amplitude'] = (index_data['high'] - index_data['low']) / index_data['close']

        features = features.fillna(0)
        return features

    def train(self, index_data: pd.DataFrame):
        """训练模型"""
        features = self.extract_features(index_data)
        labels = (index_data['close'].shift(-1) > index_data['close']).astype(int)

        valid_idx = ~(features.isna().any(axis=1) | labels.isna())
        X = features[valid_idx]
        y = labels[valid_idx]

        if len(X) > LAYER3_SVM_TRAIN_PERIOD:
            X = X.tail(LAYER3_SVM_TRAIN_PERIOD)
            y = y.tail(LAYER3_SVM_TRAIN_PERIOD)

        self.model = SVC(**LAYER3_SVM_PARAMS)
        self.model.fit(X, y)

    def predict(self, index_data: pd.DataFrame) -> dict:
        """预测"""
        self.train(index_data)

        features = self.extract_features(index_data)
        latest_features = features.iloc[[-1]]

        prediction = self.model.predict(latest_features)[0]
        probability = self.model.predict_proba(latest_features)[0][1]

        if probability >= 0.7:
            signal = 'strong_bullish'
        elif probability >= 0.55:
            signal = 'bullish'
        elif probability >= 0.45:
            signal = 'neutral'
        else:
            signal = 'bearish'

        return {
            'signal': signal,
            'prediction': prediction,
            'probability': probability
        }
