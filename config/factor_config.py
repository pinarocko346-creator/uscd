"""
因子配置文件
包含因子权重、计算参数、筛选阈值等
"""

# ============================================================================
# 第一层：基石层因子配置
# ============================================================================

# 因子权重（总和为1.0）
LAYER1_FACTOR_WEIGHTS = {
    'PE': 0.25,  # 市盈率
    'PB': 0.25,  # 市净率
    'ROE': 0.20,  # 净资产收益率
    'GrossMargin': 0.15,  # 毛利率
    'Momentum': 0.15  # 动量因子
}

# 因子方向（1表示越大越好，-1表示越小越好）
LAYER1_FACTOR_DIRECTION = {
    'PE': -1,  # 市盈率越低越好
    'PB': -1,  # 市净率越低越好
    'ROE': 1,  # ROE越高越好
    'GrossMargin': 1,  # 毛利率越高越好
    'Momentum': 1  # 动量越高越好（适度）
}

# 因子筛选阈值
LAYER1_FACTOR_FILTERS = {
    'PE': {'min': 0, 'max': 50},  # PE在0-50之间
    'PB': {'min': 0, 'max': 10},  # PB在0-10之间
    'ROE': {'min': 0.05, 'max': None},  # ROE>5%
    'MarketCap': {'min': 10000000000, 'max': None}  # 流通市值>100亿
}

# 动量因子参数
LAYER1_MOMENTUM_PERIOD = 20  # 20日动量

# 因子标准化方法：'zscore', 'minmax', 'rank'
LAYER1_STANDARDIZE_METHOD = 'zscore'

# 因子去极值参数
LAYER1_WINSORIZE_LOWER = 0.01  # 下分位数1%
LAYER1_WINSORIZE_UPPER = 0.99  # 上分位数99%

# ============================================================================
# 第二层：轮动层因子配置
# ============================================================================

# 候选因子列表（从中选出IC值最高的5个）
LAYER2_CANDIDATE_FACTORS = [
    'PE',  # 市盈率
    'PB',  # 市净率
    'PS',  # 市销率
    'ROE',  # 净资产收益率
    'ROA',  # 总资产收益率
    'GrossMargin',  # 毛利率
    'Momentum_20',  # 20日动量
    'Momentum_60'  # 60日动量
]

# 黄金因子数量
LAYER2_GOLDEN_FACTOR_COUNT = 5

# IC值计算周期
LAYER2_IC_PERIOD = 60  # 过去60天

# IC值最小阈值（低于此值的因子不选）
LAYER2_IC_MIN_THRESHOLD = 0.02

# 随机森林参数
LAYER2_RF_PARAMS = {
    'n_estimators': 100,  # 树的数量
    'max_depth': 5,  # 最大深度
    'min_samples_split': 10,  # 最小分裂样本数
    'min_samples_leaf': 5,  # 最小叶子节点样本数
    'random_state': 42  # 随机种子
}

# 训练数据周期
LAYER2_TRAIN_PERIOD = 120  # 过去120天

# 预测周期
LAYER2_PREDICT_PERIOD = 5  # 预测未来5日收益

# 过拟合检测阈值
LAYER2_OVERFIT_R2_THRESHOLD = 0.85  # R²>0.85视为过拟合

# ============================================================================
# 第三层：择时层因子配置
# ============================================================================

# KNN模型参数
LAYER3_KNN_PARAMS = {
    'n_neighbors': 5,  # K值
    'weights': 'distance',  # 权重方式
    'metric': 'euclidean'  # 距离度量
}

# KNN特征列表
LAYER3_KNN_FEATURES = [
    'return_1d',  # 前1日涨跌幅
    'return_2d',  # 前2日涨跌幅
    'return_3d',  # 前3日涨跌幅
    'return_5d',  # 前5日涨跌幅
    'return_10d',  # 前10日涨跌幅
    'volume_ratio',  # 成交量比率
    'rsi_14',  # RSI(14)
    'macd_hist',  # MACD柱状图
    'ma_deviation_20',  # 20日均线偏离度
]

# KNN训练数据周期
LAYER3_KNN_TRAIN_PERIOD = 500  # 过去500个交易日

# SVM模型参数
LAYER3_SVM_PARAMS = {
    'C': 1.0,  # 正则化强度
    'kernel': 'rbf',  # 核函数
    'gamma': 'scale',  # 核系数
    'probability': True  # 输出概率
}

# SVM特征列表（在KNN基础上增加）
LAYER3_SVM_EXTRA_FEATURES = [
    'amplitude',  # 振幅
    'late_return',  # 尾盘涨跌幅
    'north_flow',  # 北向资金流向
    'margin_balance_change'  # 融资余额变化
]

# SVM训练数据周期
LAYER3_SVM_TRAIN_PERIOD = 240  # 过去240个交易日

# SVM概率阈值
LAYER3_SVM_PROB_THRESHOLDS = {
    'strong': 0.7,  # 强信号
    'medium': 0.55,  # 中等信号
    'weak': 0.45  # 弱信号
}

# NLP情绪分析参数
LAYER3_NLP_PARAMS = {
    'sources': ['xueqiu', 'eastmoney'],  # 数据源
    'comment_count': 200,  # 每个源抓取评论数
    'time_range': 'today'  # 时间范围
}

# NLP情绪阈值
LAYER3_NLP_SENTIMENT_THRESHOLDS = {
    'extreme_bullish': 0.8,  # 极度乐观
    'bullish': 0.6,  # 乐观
    'neutral_high': 0.6,  # 中性偏多
    'neutral_low': 0.4,  # 中性偏空
    'bearish': 0.2,  # 悲观
    'extreme_bearish': 0.2  # 极度悲观
}

# ============================================================================
# 通用因子配置
# ============================================================================

# 技术指标参数
TECHNICAL_INDICATORS = {
    'RSI': {'period': 14},
    'MACD': {'fast': 12, 'slow': 26, 'signal': 9},
    'MA': {'periods': [5, 10, 20, 60]},
    'BOLL': {'period': 20, 'std': 2}
}

# 因子更新频率
FACTOR_UPDATE_FREQ = 'daily'  # 每日更新
