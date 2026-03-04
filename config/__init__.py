"""
配置模块初始化文件
"""

from .system_config import *
from .factor_config import *
from .risk_config import *

__all__ = [
    # 系统配置
    'TOTAL_CAPITAL',
    'LAYER1_WEIGHT',
    'LAYER2_WEIGHT',
    'LAYER3_WEIGHT',
    'DATA_SOURCE',

    # 因子配置
    'LAYER1_FACTOR_WEIGHTS',
    'LAYER2_CANDIDATE_FACTORS',
    'LAYER3_KNN_PARAMS',

    # 风险配置
    'LAYER1_SINGLE_STOCK_STOP_LOSS',
    'LAYER2_MAX_TURNOVER_RATE',
    'LAYER3_STOP_LOSS',
]
