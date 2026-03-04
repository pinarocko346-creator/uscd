# DY 选股系统 v2.0 更新说明

## 🎉 重大更新

DY 选股系统现已升级到 v2.0，新增了完整的策略回测、对比分析和信号追踪功能！

## ✨ 新增功能

### 1. 策略回测引擎 🚀

完整的回测系统，支持历史数据验证策略有效性。

**核心功能：**
- 单股票回测
- 投资组合回测
- 完整交易记录
- 资金曲线追踪
- 回撤分析

**使用方式：**
```python
from utils.dy_backtest import BacktestEngine

engine = BacktestEngine(initial_capital=100000)
result = engine.backtest_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategy='stable'
)
```

### 2. 策略组合管理 📊

灵活的策略管理系统，支持自定义策略和组合。

**核心功能：**
- 4 个预定义策略
- 自定义策略创建
- 策略组合管理
- 策略参数配置

**预定义策略：**
- 激进策略：买入信号（高风险高收益）
- 稳健策略：买入 + UP1（平衡风险收益）
- 最强策略：买入 + UP3（低风险稳定收益）
- 保守策略：买入 + UP1 + UP2（极低风险）

**使用方式：**
```python
from utils.dy_strategy_manager import StrategyManager

manager = StrategyManager()

# 创建自定义策略
custom = manager.create_custom_strategy(
    name='我的策略',
    description='买入 + UP1 + UP2',
    conditions={'buy': True, 'up1': True, 'up2': True}
)

manager.save_strategy('my_strategy', custom)
```

### 3. 历史信号追踪 📈

完整的信号记录和追踪系统，分析策略历史表现。

**核心功能：**
- 信号自动记录
- 历史查询
- 表现追踪
- 统计分析
- 最佳表现股票

**使用方式：**
```python
from utils.dy_signal_tracker import SignalTracker

tracker = SignalTracker()

# 保存信号
tracker.save_signal({
    'date': '2024-01-15',
    'symbol': 'AAPL',
    'price': 185.50,
    'buy': True,
    'up1': True
})

# 查询统计
stats = tracker.get_signal_statistics(days=30)
```

### 4. 性能统计分析 📉

专业的性能指标计算和可视化。

**核心指标：**
- 总收益率 / 年化收益率
- 最大回撤
- 夏普比率
- 索提诺比率
- 卡玛比率
- 盈亏比
- 胜率统计

**图表生成：**
- 资金曲线图
- 回撤曲线图
- 交易分析图
- 收益分布图

**使用方式：**
```python
from utils.dy_performance import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()
metrics = analyzer.calculate_metrics(backtest_result)

# 生成图表
analyzer.plot_equity_curve(backtest_result)
analyzer.plot_trade_analysis(backtest_result)

# 生成 HTML 报告
analyzer.generate_report(backtest_result, metrics)
```

### 5. 策略对比分析 🔄

多策略同时对比，找出最佳策略。

**核心功能：**
- 多策略对比
- 综合排名评分
- 可视化对比图表
- 最佳策略推荐

**使用方式：**
```python
from utils.dy_comparator import StrategyComparator

comparator = StrategyComparator()

# 对比策略
comparison = comparator.compare_strategies_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategies=['buy_signal', 'stable', 'strongest']
)

# 生成对比报告
comparator.generate_comparison_report(comparison)
```

### 6. Web 界面升级 🌐

全新的回测分析页面，提供完整的可视化界面。

**新增页面：**
- 策略回测页面
- 策略对比页面
- 信号追踪页面
- 策略管理页面

**访问地址：**
- http://localhost:5001/backtest

## 📁 新增文件

### 核心模块
```
utils/
├── dy_backtest.py           # 回测引擎
├── dy_strategy_manager.py   # 策略管理器
├── dy_signal_tracker.py     # 信号追踪器
├── dy_performance.py        # 性能分析器
└── dy_comparator.py         # 策略对比器
```

### Web 界面
```
templates/dy/
└── dy_backtest.html         # 回测分析页面
```

### 文档
```
DY_BACKTEST_GUIDE.md         # 完整使用指南
DY_UPDATE_v2.0.md            # 本更新说明
```

### 测试脚本
```
test_dy_backtest.py          # 功能测试脚本
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install matplotlib seaborn
```

### 2. 运行测试

```bash
python test_dy_backtest.py
```

### 3. 启动 Web 服务

```bash
./start_dy_web.sh
```

### 4. 访问界面

打开浏览器访问：
- 回测分析: http://localhost:5001/backtest
- 主页: http://localhost:5001

## 📊 使用示例

### 示例 1：快速回测

```python
from utils.dy_backtest import BacktestEngine

engine = BacktestEngine(initial_capital=100000)

result = engine.backtest_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategy='stable'
)

print(f"总收益率: {result['total_return_pct']:.2f}%")
print(f"胜率: {result['win_rate_pct']:.2f}%")
```

### 示例 2：对比策略

```python
from utils.dy_comparator import StrategyComparator

comparator = StrategyComparator()

comparison = comparator.compare_strategies_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01'
)

print(comparison)
```

### 示例 3：追踪信号

```python
from utils.dy_signal_tracker import SignalTracker

tracker = SignalTracker()

# 保存今日信号
tracker.save_signal({
    'date': '2024-01-15',
    'symbol': 'AAPL',
    'price': 185.50,
    'buy': True,
    'up1': True
})

# 查询统计
stats = tracker.get_signal_statistics(days=30)
print(f"买入信号: {stats['buy_signals']}")
```

## 🔌 新增 API

### 回测 API
- `POST /api/backtest` - 运行回测
- `POST /api/compare_strategies` - 对比策略

### 信号追踪 API
- `POST /api/save_signals` - 保存信号
- `GET /api/signal_history` - 查询历史信号
- `GET /api/signal_statistics` - 获取统计信息

### 策略管理 API
- `GET /api/strategies` - 列出所有策略
- `POST /api/strategy` - 创建策略
- `DELETE /api/strategy/<id>` - 删除策略

### 报告 API
- `GET /api/reports/<filename>` - 获取报告文件

## 📈 性能优化

- 使用 SQLite 数据库存储信号，查询速度快
- 图表生成使用非交互式后端，节省资源
- 支持并发回测，提高效率
- 缓存策略配置，减少 I/O 操作

## 🔧 技术栈

- **回测引擎**: pandas, numpy, yfinance
- **数据存储**: SQLite
- **图表生成**: matplotlib, seaborn
- **Web 框架**: Flask
- **前端**: HTML5, CSS3, JavaScript

## 📝 注意事项

1. **数据要求**: 回测需要至少 100 天的历史数据
2. **网络连接**: 使用 yfinance 需要网络连接
3. **图表依赖**: 需要安装 matplotlib 和 seaborn
4. **数据库**: 信号追踪会在 data/ 目录创建数据库文件
5. **报告目录**: 图表和报告保存在 reports/ 目录

## 🐛 已知问题

1. 大量股票回测可能需要较长时间
2. 图表中文显示可能需要配置字体
3. 某些股票可能因数据不足导致回测失败

## 🔮 未来计划

- [ ] 支持更多技术指标
- [ ] 添加机器学习策略
- [ ] 实时信号推送
- [ ] 移动端适配
- [ ] 多账户管理
- [ ] 风险管理模块

## 📚 文档索引

- [完整使用指南](DY_BACKTEST_GUIDE.md)
- [策略指南](DY_STRATEGY_GUIDE.md)
- [快速参考](DY_QUICK_REFERENCE.md)
- [项目总结](DY_PROJECT_SUMMARY.md)

## 🙏 致谢

感谢所有使用和支持 DY 选股系统的用户！

## 📞 反馈

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- Email: support@dy-quant.com

---

**版本**: v2.0
**发布日期**: 2026-03-04
**更新内容**: 新增策略回测、对比分析、信号追踪等完整功能
**兼容性**: 完全向后兼容 v1.x

🎉 **立即体验新功能！**

```bash
# 运行测试
python test_dy_backtest.py

# 启动服务
./start_dy_web.sh

# 访问回测页面
open http://localhost:5001/backtest
```
