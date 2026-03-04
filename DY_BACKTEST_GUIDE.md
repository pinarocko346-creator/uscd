# DY 策略回测与分析系统 - 完整指南

## 📋 目录

1. [功能概览](#功能概览)
2. [快速开始](#快速开始)
3. [策略回测](#策略回测)
4. [策略对比](#策略对比)
5. [信号追踪](#信号追踪)
6. [策略管理](#策略管理)
7. [API 文档](#api-文档)
8. [使用示例](#使用示例)

## 🎯 功能概览

DY 策略回测与分析系统提供以下核心功能：

### 1. 策略回测
- 单股票历史回测
- 多股票组合回测
- 完整的性能指标计算
- 资金曲线和回撤分析
- 交易明细记录

### 2. 策略对比
- 多策略同时对比
- 综合排名评分
- 可视化对比图表
- 最佳策略推荐

### 3. 信号追踪
- 历史信号记录
- 信号表现追踪
- 统计分析报告
- 最佳表现股票

### 4. 策略管理
- 预定义策略库
- 自定义策略创建
- 策略组合管理
- 策略参数配置

### 5. 性能分析
- 夏普比率
- 索提诺比率
- 卡玛比率
- 盈亏比
- 最大回撤
- 胜率统计

## 🚀 快速开始

### 安装依赖

```bash
cd /Users/apple/three-layer-quant-system
pip install -r requirements.txt
```

确保 requirements.txt 包含以下依赖：
```
flask
pandas
numpy
yfinance
matplotlib
seaborn
```

### 启动服务

```bash
# 启动 Web 服务
./start_dy_web.sh

# 或者直接运行
python dy_web_server.py
```

### 访问界面

打开浏览器访问：
- 主页（选股器）: http://localhost:5001
- 回测分析: http://localhost:5001/backtest
- 高级功能: http://localhost:5001/advanced

## 📊 策略回测

### Web 界面使用

1. 访问 http://localhost:5001/backtest
2. 选择"策略回测"标签
3. 输入参数：
   - 股票代码（如 AAPL）
   - 开始日期
   - 结束日期
   - 选择策略
4. 点击"开始回测"
5. 查看结果和图表

### Python 代码使用

```python
from utils.dy_backtest import BacktestEngine

# 创建回测引擎
engine = BacktestEngine(initial_capital=100000)

# 回测单个股票
result = engine.backtest_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategy='stable'  # 'buy_signal', 'stable', 'strongest'
)

# 查看结果
print(f"总收益率: {result['total_return_pct']:.2f}%")
print(f"最大回撤: {result['max_drawdown_pct']:.2f}%")
print(f"胜率: {result['win_rate_pct']:.2f}%")
print(f"交易次数: {result['total_trades']}")
```

### 回测投资组合

```python
# 回测多个股票
symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

portfolio_result = engine.backtest_portfolio(
    symbols=symbols,
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategy='stable',
    max_positions=5
)

print(f"平均收益率: {portfolio_result['avg_total_return_pct']:.2f}%")
print(f"平均胜率: {portfolio_result['avg_win_rate_pct']:.2f}%")
```

## 🔄 策略对比

### Web 界面使用

1. 访问回测页面
2. 选择"策略对比"标签
3. 输入股票代码和日期范围
4. 点击"开始对比"
5. 查看对比表格和图表

### Python 代码使用

```python
from utils.dy_comparator import StrategyComparator

# 创建对比器
comparator = StrategyComparator(initial_capital=100000)

# 对比单个股票的多个策略
comparison = comparator.compare_strategies_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategies=['buy_signal', 'stable', 'strongest']
)

print(comparison)

# 生成对比报告
report_path = comparator.generate_comparison_report(comparison)
print(f"报告已生成: {report_path}")
```

### 找出最佳策略

```python
# 自动找出最佳策略
best = comparator.find_best_strategy(
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    start_date='2023-01-01',
    end_date='2024-01-01',
    criterion='total_return'  # 'total_return', 'sharpe_ratio', 'win_rate'
)

print(f"最佳策略: {best['strategy']}")
print(f"评分: {best['value']:.2f}")
```

## 📈 信号追踪

### 保存信号

```python
from utils.dy_signal_tracker import SignalTracker

# 创建追踪器
tracker = SignalTracker()

# 保存单个信号
signal = {
    'date': '2024-01-15',
    'symbol': 'AAPL',
    'price': 185.50,
    'buy': True,
    'sell': False,
    'up1': True,
    'up2': False,
    'up3': False,
    'down1': False,
    'down2': False,
    'down3': False
}

tracker.save_signal(signal)
```

### 查询历史信号

```python
# 查询特定股票的信号
signals = tracker.get_signals(
    symbol='AAPL',
    start_date='2024-01-01',
    end_date='2024-12-31',
    signal_type='buy'  # 'buy', 'sell', 'up1', etc.
)

print(f"找到 {len(signals)} 条信号")
```

### 获取统计信息

```python
# 获取最近 30 天的统计
stats = tracker.get_signal_statistics(days=30)

print(f"总信号数: {stats['total_signals']}")
print(f"买入信号: {stats['buy_signals']}")
print(f"卖出信号: {stats['sell_signals']}")

# 如果有表现数据
if 'performance' in stats:
    perf = stats['performance']
    print(f"平均收益: {perf['avg_return_pct']:.2f}%")
    print(f"胜率: {perf['win_rate_pct']:.2f}%")
```

### 追踪信号表现

```python
# 开始追踪一个信号
tracker.track_signal_performance(
    signal_id=1,
    symbol='AAPL',
    signal_date='2024-01-15',
    signal_type='buy',
    entry_price=185.50
)

# 关闭追踪（卖出时）
tracker.close_signal_performance(
    performance_id=1,
    exit_price=195.00,
    exit_date='2024-01-25'
)
```

## 🎯 策略管理

### 预定义策略

系统提供 4 个预定义策略：

1. **激进策略** (buy_signal)
   - 条件：买入信号
   - 风险：高
   - 预期收益：5-15%
   - 持仓周期：1-5天

2. **稳健策略** (stable)
   - 条件：买入信号 + UP1
   - 风险：中
   - 预期收益：8-20%
   - 持仓周期：5-15天

3. **最强策略** (strongest)
   - 条件：买入信号 + UP3
   - 风险：低
   - 预期收益：15-40%
   - 持仓周期：15-30天

4. **保守策略** (conservative)
   - 条件：买入信号 + UP1 + UP2
   - 风险：极低
   - 预期收益：10-25%
   - 持仓周期：10-20天

### 创建自定义策略

```python
from utils.dy_strategy_manager import StrategyManager

# 创建管理器
manager = StrategyManager()

# 创建自定义策略
custom_strategy = manager.create_custom_strategy(
    name='我的策略',
    description='买入 + UP1 + UP2',
    conditions={
        'buy': True,
        'up1': True,
        'up2': True
    },
    risk_level='low',
    expected_return='10-25%',
    holding_period='10-20天'
)

# 保存策略
manager.save_strategy('my_strategy', custom_strategy)
```

### 创建策略组合

```python
# 创建组合
portfolio = manager.create_portfolio(
    name='平衡组合',
    strategies=[
        {'id': 'buy_signal', 'weight': 0.3},
        {'id': 'stable', 'weight': 0.5},
        {'id': 'strongest', 'weight': 0.2}
    ]
)

# 保存组合
manager.save_portfolio('balanced', portfolio)
```

### 使用策略筛选股票

```python
# 假设你有一个股票列表
stocks = [
    {'symbol': 'AAPL', 'buy': True, 'up1': True, 'up2': False},
    {'symbol': 'MSFT', 'buy': True, 'up1': True, 'up2': True},
    {'symbol': 'GOOGL', 'buy': False, 'up1': False, 'up2': False}
]

# 使用策略筛选
filtered = manager.filter_stocks_by_strategy(stocks, 'stable')
print(f"符合稳健策略的股票: {[s['symbol'] for s in filtered]}")
```

## 📊 性能分析

### 生成性能报告

```python
from utils.dy_performance import PerformanceAnalyzer

# 创建分析器
analyzer = PerformanceAnalyzer()

# 计算性能指标
metrics = analyzer.calculate_metrics(backtest_result)

print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"索提诺比率: {metrics['sortino_ratio']:.2f}")
print(f"卡玛比率: {metrics['calmar_ratio']:.2f}")
print(f"盈亏比: {metrics['profit_factor']:.2f}")
```

### 生成图表

```python
# 生成资金曲线图
equity_chart = analyzer.plot_equity_curve(
    backtest_result,
    'equity_curve.png'
)

# 生成交易分析图
trade_chart = analyzer.plot_trade_analysis(
    backtest_result,
    'trade_analysis.png'
)

# 生成策略对比图
comparison_chart = analyzer.plot_strategy_comparison(
    comparison_df,
    'strategy_comparison.png'
)
```

### 生成 HTML 报告

```python
# 生成完整的 HTML 报告
report_path = analyzer.generate_report(
    backtest_result,
    metrics,
    'backtest_report.html'
)

print(f"报告已生成: {report_path}")
```

## 🔌 API 文档

### 回测 API

**POST /api/backtest**

请求体：
```json
{
  "symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "strategy": "stable"
}
```

响应：
```json
{
  "success": true,
  "result": {
    "symbol": "AAPL",
    "total_return_pct": 15.5,
    "annual_return_pct": 15.8,
    "max_drawdown_pct": -8.2,
    "sharpe_ratio": 1.45,
    "win_rate_pct": 65.0,
    "total_trades": 12
  }
}
```

### 策略对比 API

**POST /api/compare_strategies**

请求体：
```json
{
  "symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "strategies": ["buy_signal", "stable", "strongest"]
}
```

### 信号历史 API

**GET /api/signal_history?symbol=AAPL&start_date=2024-01-01**

### 信号统计 API

**GET /api/signal_statistics?days=30**

### 策略列表 API

**GET /api/strategies**

### 创建策略 API

**POST /api/strategy**

请求体：
```json
{
  "name": "我的策略",
  "description": "买入 + UP1",
  "conditions": {
    "buy": true,
    "up1": true
  },
  "risk_level": "medium"
}
```

## 💡 使用示例

### 示例 1：完整的回测流程

```python
from utils.dy_backtest import BacktestEngine
from utils.dy_performance import PerformanceAnalyzer

# 1. 创建引擎
engine = BacktestEngine(initial_capital=100000)

# 2. 运行回测
result = engine.backtest_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategy='stable'
)

# 3. 分析性能
analyzer = PerformanceAnalyzer()
metrics = analyzer.calculate_metrics(result)

# 4. 生成图表
analyzer.plot_equity_curve(result)
analyzer.plot_trade_analysis(result)

# 5. 生成报告
analyzer.generate_report(result, metrics)

print("回测完成！")
```

### 示例 2：对比多个策略并选择最佳

```python
from utils.dy_comparator import StrategyComparator

# 1. 创建对比器
comparator = StrategyComparator()

# 2. 对比策略
comparison = comparator.compare_strategies_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01'
)

# 3. 排名
ranked = comparator.rank_strategies(comparison)

# 4. 找出最佳
best = ranked.iloc[0]
print(f"最佳策略: {best['strategy']}")
print(f"综合得分: {best['score']:.2f}")

# 5. 生成报告
comparator.generate_comparison_report(comparison)
```

### 示例 3：信号追踪和分析

```python
from utils.dy_signal_tracker import SignalTracker
from utils.dy_screener import DYScreener

# 1. 运行选股
screener = DYScreener()
results = screener.screen_stocks(['AAPL', 'MSFT', 'GOOGL'])

# 2. 保存信号
tracker = SignalTracker()
for result in results:
    signal = {
        'date': '2024-01-15',
        'symbol': result['symbol'],
        'price': result['price'],
        'buy': result['buy'],
        'sell': result['sell'],
        'up1': result['up1'],
        'up2': result['up2'],
        'up3': result['up3'],
        'down1': result['down1'],
        'down2': result['down2'],
        'down3': result['down3']
    }
    tracker.save_signal(signal)

# 3. 查询统计
stats = tracker.get_signal_statistics(days=30)
print(f"最近 30 天买入信号: {stats['buy_signals']}")

# 4. 查看最佳表现
top_performers = tracker.get_top_performers(limit=10)
print(top_performers)
```

## 📝 注意事项

1. **数据要求**：回测需要至少 100 天的历史数据
2. **性能考虑**：大量股票回测可能需要较长时间
3. **数据源**：使用 yfinance 获取数据，需要网络连接
4. **图表生成**：需要 matplotlib 和 seaborn 库
5. **数据库**：信号追踪使用 SQLite 数据库

## 🔧 故障排除

### 问题：回测失败

**解决方案**：
- 检查日期范围是否合理
- 确保股票代码正确
- 验证网络连接
- 检查数据是否充足

### 问题：图表无法生成

**解决方案**：
- 安装 matplotlib: `pip install matplotlib`
- 安装 seaborn: `pip install seaborn`
- 检查 reports 目录是否存在

### 问题：信号保存失败

**解决方案**：
- 检查 data 目录是否存在
- 验证数据库文件权限
- 确保信号数据格式正确

## 📚 更多资源

- [DY 选股器文档](DY_SCREENER_README.md)
- [策略指南](DY_STRATEGY_GUIDE.md)
- [快速参考](DY_QUICK_REFERENCE.md)
- [项目总结](DY_PROJECT_SUMMARY.md)

---

**版本**: v2.0
**更新时间**: 2026-03-04
**作者**: DY 量化团队
