"""
风险配置文件
包含止损比例、回撤阈值、预警设置等
"""

# ============================================================================
# 第一层：基石层风险配置
# ============================================================================

# 单股止损
LAYER1_SINGLE_STOCK_STOP_LOSS = -0.15  # -15%

# 组合回撤阈值
LAYER1_PORTFOLIO_DRAWDOWN_THRESHOLD = -0.20  # -20%

# 连续跑输基准阈值
LAYER1_UNDERPERFORM_MONTHS = 2  # 连续2个月

# 系统性风险应对（指数月跌幅>10%）
LAYER1_SYSTEMIC_RISK_THRESHOLD = -0.10
LAYER1_SYSTEMIC_RISK_POSITION_CUT = 0.5  # 减仓至50%

# 因子失效阈值
LAYER1_FACTOR_IC_THRESHOLD = 0.02  # IC<0.02视为失效
LAYER1_FACTOR_IC_CHECK_MONTHS = 2  # 连续2个月

# 流动性要求
LAYER1_MIN_MARKET_CAP = 10000000000  # 最小流通市值：100亿
LAYER1_MIN_DAILY_VOLUME = 50000000  # 最小日成交额：5000万

# ============================================================================
# 第二层：轮动层风险配置
# ============================================================================

# 模型过拟合检测
LAYER2_OVERFIT_R2_THRESHOLD = 0.85  # R²>0.85
LAYER2_OVERFIT_TRAIN_TEST_GAP = 0.3  # 训练集与测试集R²差距>0.3

# 黄金因子剧变预警
LAYER2_FACTOR_CHANGE_THRESHOLD = 3  # 换因子>3个

# 高换手率限制
LAYER2_MAX_TURNOVER_RATE = 0.66  # 最大换手率：66%
LAYER2_MAX_NEW_STOCKS = 10  # 最多新进入10只

# 连续亏损暂停
LAYER2_CONSECUTIVE_LOSS_WEEKS = 3  # 连续3周
LAYER2_PAUSE_WEEKS = 1  # 暂停1周

# 与基石层背离检测
LAYER2_DIVERGENCE_THRESHOLD = 0.5  # 方向相反股票占比>50%

# ============================================================================
# 第三层：择时层风险配置
# ============================================================================

# 模型冲突处理
LAYER3_MODEL_CONFLICT_ACTION = 'hold'  # 'hold', 'follow_layer1', 'reduce'

# 连续错误暂停
LAYER3_CONSECUTIVE_ERROR_DAYS = 3  # 连续3天
LAYER3_PAUSE_DAYS = 7  # 暂停7天

# 极端波动应对
LAYER3_EXTREME_VOLATILITY_THRESHOLD = 0.05  # 单日涨跌幅>5%
LAYER3_EXTREME_VOLATILITY_ACTION = 'reduce_half'  # 减仓50%

# 数据缺失处理
LAYER3_MIN_NLP_COMMENTS = 50  # 最少评论数
LAYER3_DATA_MISSING_ACTION = 'use_knn_svm'  # 只用KNN+SVM

# 黑天鹅事件
LAYER3_BLACK_SWAN_MANUAL_OVERRIDE = True  # 允许人工干预

# 择时层止损
LAYER3_STOP_LOSS = -0.03  # -3%
LAYER3_TAKE_PROFIT = 0.10  # +10%

# ============================================================================
# 三层协同风险配置
# ============================================================================

# 进攻状态（择时层满仓信号）
AGGRESSIVE_MAX_LEVERAGE = 1.3  # 最大杠杆：130%
AGGRESSIVE_LAYER1_BOOST = 0.15  # 基石层提升至65%
AGGRESSIVE_LAYER2_BOOST = 0.05  # 轮动层提升至35%
AGGRESSIVE_LAYER3_FULL = 0.20  # 择时层满仓20%

# 防守状态（择时层空仓信号）
DEFENSIVE_LAYER1_CUT = 0.25  # 基石层降至25%
DEFENSIVE_LAYER2_CUT = 0.15  # 轮动层降至15%
DEFENSIVE_LAYER3_EMPTY = 0.00  # 择时层清空
DEFENSIVE_TOTAL_POSITION = 0.40  # 总仓位：40%

# 极端恐慌状态（NLP<0.1）
PANIC_MAX_LEVERAGE = 1.3  # 最大杠杆：130%
PANIC_LAYER1_BOOST = 0.30  # 基石层提升至80%
PANIC_LAYER2_FULL = 0.30  # 轮动层满仓30%
PANIC_LAYER3_FULL = 0.20  # 择时层满仓20%
PANIC_SINGLE_STOCK_MAX = 0.05  # 单只股票最大5%
PANIC_BUY_DAYS = 3  # 分3天买入
PANIC_HARD_STOP_LOSS = -0.08  # 硬止损：-8%

# ============================================================================
# 通用风险配置
# ============================================================================

# 最大总仓位
MAX_TOTAL_POSITION = 1.3  # 130%（含杠杆）

# 最小总仓位
MIN_TOTAL_POSITION = 0.40  # 40%（防守状态）

# 单只股票最大仓位
MAX_SINGLE_STOCK_POSITION = 0.05  # 5%

# 单日最大交易量（占总资金比例）
MAX_DAILY_TRADE_VOLUME = 0.30  # 30%

# 现金储备
MIN_CASH_RESERVE = 0.05  # 最少保留5%现金

# ============================================================================
# 预警配置
# ============================================================================

# 预警级别
ALERT_LEVELS = {
    'INFO': 1,  # 信息
    'WARNING': 2,  # 警告
    'ERROR': 3,  # 错误
    'CRITICAL': 4  # 严重
}

# 预警触发条件
ALERT_TRIGGERS = {
    'single_stock_loss': {
        'threshold': -0.10,  # 单股亏损>10%
        'level': 'WARNING'
    },
    'portfolio_drawdown': {
        'threshold': -0.15,  # 组合回撤>15%
        'level': 'ERROR'
    },
    'model_error': {
        'consecutive_days': 2,  # 连续2天错误
        'level': 'WARNING'
    },
    'data_missing': {
        'level': 'WARNING'
    },
    'extreme_volatility': {
        'threshold': 0.05,  # 单日波动>5%
        'level': 'INFO'
    }
}

# 预警发送频率限制
ALERT_COOLDOWN = {
    'INFO': 3600,  # 1小时
    'WARNING': 1800,  # 30分钟
    'ERROR': 600,  # 10分钟
    'CRITICAL': 0  # 立即发送
}
