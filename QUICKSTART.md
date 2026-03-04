# 三层量化策略体系 - 快速开始

## 项目已搭建完成 ✓

恭喜！三层量化策略体系已经成功搭建。以下是项目结构和使用说明。

## 📁 项目结构

```
three-layer-quant-system/
├── config/                      # 配置文件
│   ├── system_config.py         # 系统配置（资金、数据源等）
│   ├── factor_config.py         # 因子配置（权重、参数等）
│   └── risk_config.py           # 风险配置（止损、预警等）
│
├── utils/                       # 工具模块
│   ├── data_fetcher.py          # 数据获取（支持模拟数据）
│   ├── factor_library.py        # 因子计算库
│   ├── performance_metrics.py   # 性能指标计算
│   └── logger.py                # 日志系统
│
├── layer1_cornerstone/          # 第一层：基石层
│   ├── factor_calculator.py     # 因子计算器
│   ├── stock_selector.py        # 选股器
│   ├── risk_manager.py          # 风险管理器
│   └── main.py                  # 主程序
│
├── layer2_rotation/             # 第二层：轮动层
│   ├── ic_calculator.py         # IC值计算器
│   ├── random_forest_model.py   # 随机森林模型
│   └── main.py                  # 主程序
│
├── layer3_timing/               # 第三层：择时层
│   ├── knn_model.py             # KNN模型
│   ├── svm_model.py             # SVM模型
│   ├── nlp_model.py             # NLP情绪分析
│   ├── voting_system.py         # 投票系统
│   └── main.py                  # 主程序
│
├── main.py                      # 系统主入口
├── requirements.txt             # 依赖包
└── README.md                    # 项目说明
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ~/three-layer-quant-system
pip install -r requirements.txt
```

### 2. 运行系统

```bash
# 运行完整系统（三层同时运行）
python main.py

# 单独运行某一层
python layer1_cornerstone/main.py  # 基石层
python layer2_rotation/main.py     # 轮动层
python layer3_timing/main.py       # 择时层
```

### 3. 配置系统

编辑 `config/system_config.py`：

```python
# 资金配置
TOTAL_CAPITAL = 1000000  # 总资金（元）

# 仓位配置
LAYER1_WEIGHT = 0.50  # 基石层：50%
LAYER2_WEIGHT = 0.30  # 轮动层：30%
LAYER3_WEIGHT = 0.20  # 择时层：20%

# 数据源
DATA_SOURCE = 'mock'  # 'mock'=模拟数据, 'tushare'=Tushare, 'akshare'=AKShare
```

## 📊 三层策略说明

### 第一层：基石层（50%仓位，月频）

**策略**：多因子回归选股
- **股票池**：沪深300成分股
- **因子**：PE、PB、ROE、毛利率、动量
- **持仓**：20只股票，等权重
- **调仓**：每月第一个交易日

**风险控制**：
- 单股止损：-15%
- 组合回撤：-20%
- 系统性风险应对

### 第二层：轮动层（30%仓位，周频）

**策略**：随机森林动态因子
- **股票池**：中证500成分股
- **方法**：每周选出IC值最高的5个黄金因子
- **持仓**：15只股票
- **调仓**：每周一

**风险控制**：
- 过拟合检测
- 换手率限制：<66%
- 因子剧变预警

### 第三层：择时层（20%仓位，日频）

**策略**：KNN+SVM+NLP三模型投票
- **标的**：沪深300ETF
- **模型**：
  - KNN：历史相似度匹配
  - SVM：技术指标分类
  - NLP：市场情绪分析
- **决策**：三模型投票
- **调仓**：每日

**投票规则**：
- 3票看多 → 满仓（20%）
- 2票看多 → 半仓（10%）
- 1票看多 → 观望（0%）
- 0票看多 → 空仓

## 🔧 自定义配置

### 修改因子权重

编辑 `config/factor_config.py`：

```python
LAYER1_FACTOR_WEIGHTS = {
    'PE': 0.25,
    'PB': 0.25,
    'ROE': 0.20,
    'GrossMargin': 0.15,
    'Momentum': 0.15
}
```

### 修改风险参数

编辑 `config/risk_config.py`：

```python
# 单股止损
LAYER1_SINGLE_STOCK_STOP_LOSS = -0.15  # -15%

# 组合回撤阈值
LAYER1_PORTFOLIO_DRAWDOWN_THRESHOLD = -0.20  # -20%
```

## 📝 日志查看

日志文件保存在 `logs/` 目录：

```bash
# 查看系统日志
tail -f logs/system_20260303.log

# 查看各层日志
tail -f logs/layer1_cornerstone_20260303.log
tail -f logs/layer2_rotation_20260303.log
tail -f logs/layer3_timing_20260303.log
```

## 🎯 运行示例

运行 `main.py` 后，你会看到：

```
================================================================================
三层量化交易系统
================================================================================

系统说明:
  第一层（基石层）: 多因子回归，月频调仓，50%仓位
  第二层（轮动层）: 随机森林，周频调仓，30%仓位
  第三层（择时层）: KNN+SVM+NLP，日频调仓，20%仓位

================================================================================

>>> 运行第一层：基石层
  获取到 300 只股票
  选中 20 只股票
  ✓ 第一层运行成功

>>> 运行第二层：轮动层
  黄金因子: ['ROE', 'Momentum_20', 'PE', 'GrossMargin', 'PB']
  选中 15 只股票
  ✓ 第二层运行成功

>>> 运行第三层：择时层
  KNN信号: bullish
  SVM信号: bullish
  NLP情绪: neutral
  投票结果: half_position (50%)
  ✓ 第三层运行成功

================================================================================
运行结果
================================================================================
layer1: ✓ 成功
layer2: ✓ 成功
layer3: ✓ 成功
================================================================================
```

## ⚠️ 重要说明

### 当前状态

1. **数据源**：默认使用模拟数据（`DATA_SOURCE = 'mock'`）
2. **实盘使用**：需要配置真实数据源（Tushare或AKShare）
3. **回测功能**：基础框架已搭建，可根据需要扩展

### 接入真实数据

如果要使用真实数据，需要：

1. 安装数据源包：
```bash
pip install tushare  # 或 pip install akshare
```

2. 修改配置：
```python
# config/system_config.py
DATA_SOURCE = 'tushare'  # 或 'akshare'
TUSHARE_TOKEN = 'your_token_here'  # 如果使用tushare
```

3. 实现真实数据获取逻辑（在 `utils/data_fetcher.py` 中）

## 📈 预期效果

| 指标 | 目标值 |
|------|--------|
| 年化收益率 | 20-30% |
| 最大回撤 | 15-20% |
| 夏普比率 | 1.5-2.0 |
| 胜率 | 60%+ |

## 🎓 下一步

1. **回测验证**：使用历史数据回测策略效果
2. **参数优化**：根据回测结果调整因子权重和模型参数
3. **风险管理**：完善风险控制逻辑
4. **实盘测试**：小资金测试3个月以上
5. **监控系统**：添加实时监控和报警功能

## 📞 技术支持

- 查看日志：`logs/` 目录
- 修改配置：`config/` 目录
- 扩展功能：各层的 `main.py` 文件

---

**免责声明**：本系统仅供学习和研究使用。实盘交易风险自负。
