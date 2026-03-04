# 🚀 DY 策略回测系统 v2.0

专业的量化策略回测、对比分析和信号追踪系统

## ✨ 核心功能

### 1. 策略回测 📊
- 单股票历史回测
- 投资组合回测
- 完整交易记录
- 资金曲线分析
- 回撤计算

### 2. 策略管理 🎯
- 4 个预定义策略
- 自定义策略创建
- 策略组合管理
- 灵活参数配置

### 3. 信号追踪 📈
- 历史信号记录
- 表现追踪分析
- 统计报告生成
- 最佳股票推荐

### 4. 性能分析 📉
- 夏普比率
- 索提诺比率
- 卡玛比率
- 盈亏比分析
- 可视化图表

### 5. 策略对比 🔄
- 多策略对比
- 综合排名
- 最佳策略推荐
- 对比报告生成

## 🎯 预定义策略

| 策略 | 条件 | 风险 | 预期收益 | 持仓周期 |
|-----|------|------|---------|---------|
| 激进策略 | 买入信号 | 高 | 5-15% | 1-5天 |
| 稳健策略 | 买入+UP1 | 中 | 8-20% | 5-15天 |
| 最强策略 | 买入+UP3 | 低 | 15-40% | 15-30天 |
| 保守策略 | 买入+UP1+UP2 | 极低 | 10-25% | 10-20天 |

## 🚀 快速开始

### 安装依赖

```bash
pip install flask pandas numpy yfinance matplotlib seaborn
```

### 运行示例

```bash
# 快速示例
python dy_backtest_example.py

# 完整测试
python test_dy_backtest.py
```

### 启动 Web 服务

```bash
./start_dy_web.sh
```

访问: http://localhost:5001/backtest

## 💻 使用示例

### 策略回测

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

### 策略对比

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

### 信号追踪

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

### 自定义策略

```python
from utils.dy_strategy_manager import StrategyManager

manager = StrategyManager()

# 创建策略
custom = manager.create_custom_strategy(
    name='我的策略',
    description='买入 + UP1 + UP2',
    conditions={'buy': True, 'up1': True, 'up2': True}
)

manager.save_strategy('my_strategy', custom)
```

## 📊 性能指标

系统计算以下性能指标：

- **收益指标**: 总收益率、年化收益率
- **风险指标**: 最大回撤、波动率
- **风险调整收益**: 夏普比率、索提诺比率、卡玛比率
- **交易统计**: 胜率、盈亏比、交易次数
- **连续表现**: 最大连续盈利/亏损

## 🌐 Web 界面

访问 http://localhost:5001/backtest 使用 Web 界面：

- **策略回测**: 输入股票代码和日期，一键回测
- **策略对比**: 同时对比多个策略，找出最佳
- **信号追踪**: 查看历史信号统计和表现
- **策略管理**: 创建和管理自定义策略

## 📁 项目结构

```
utils/
├── dy_backtest.py           # 回测引擎
├── dy_strategy_manager.py   # 策略管理
├── dy_signal_tracker.py     # 信号追踪
├── dy_performance.py        # 性能分析
└── dy_comparator.py         # 策略对比

templates/dy/
└── dy_backtest.html         # Web 界面

config/strategies/           # 策略配置
data/                        # 信号数据库
reports/                     # 报告和图表
```

## 🔌 API 端点

### 回测 API
- `POST /api/backtest` - 运行回测
- `POST /api/compare_strategies` - 对比策略

### 信号 API
- `POST /api/save_signals` - 保存信号
- `GET /api/signal_history` - 查询历史
- `GET /api/signal_statistics` - 获取统计

### 策略 API
- `GET /api/strategies` - 列出策略
- `POST /api/strategy` - 创建策略
- `DELETE /api/strategy/<id>` - 删除策略

## 📚 文档

- [完整使用指南](DY_BACKTEST_GUIDE.md) - 详细的使用说明
- [更新说明](DY_UPDATE_v2.0.md) - v2.0 新增功能
- [策略指南](DY_STRATEGY_GUIDE.md) - 策略使用指南
- [快速参考](DY_QUICK_REFERENCE.md) - 快速查询手册

## 🎓 示例脚本

- `dy_backtest_example.py` - 快速示例
- `test_dy_backtest.py` - 完整测试

## ⚙️ 配置

### 回测参数

```python
BacktestEngine(
    initial_capital=100000,  # 初始资金
    commission=0.001         # 手续费率 (0.1%)
)
```

### 策略条件

可用的信号条件：
- `buy`: 买入信号（底背离 + DIFF 上穿 DEA）
- `sell`: 卖出信号（顶背离 + DIFF 下穿 DEA）
- `up1`: 突破蓝带上轨
- `up2`: 突破黄带上轨
- `up3`: 蓝带突破黄带
- `down1`: 跌破蓝带下轨
- `down2`: 跌破黄带下轨
- `down3`: 蓝带跌破黄带

## 📈 图表示例

系统自动生成以下图表：

1. **资金曲线图** - 显示资金变化和回撤
2. **交易分析图** - 每笔交易收益和分布
3. **策略对比图** - 多策略性能对比
4. **收益分布图** - 收益率分布直方图

## 🔧 技术栈

- **Python 3.8+**
- **pandas** - 数据处理
- **numpy** - 数值计算
- **yfinance** - 股票数据
- **matplotlib** - 图表生成
- **seaborn** - 高级可视化
- **Flask** - Web 框架
- **SQLite** - 数据存储

## 📝 注意事项

1. 回测需要至少 100 天的历史数据
2. 使用 yfinance 需要网络连接
3. 首次运行可能需要下载数据
4. 图表生成需要 matplotlib 和 seaborn
5. 信号追踪使用 SQLite 数据库

## 🐛 故障排除

### 回测失败
- 检查股票代码是否正确
- 确保日期范围合理
- 验证网络连接

### 图表无法生成
- 安装 matplotlib: `pip install matplotlib`
- 安装 seaborn: `pip install seaborn`
- 检查 reports 目录权限

### 信号保存失败
- 检查 data 目录是否存在
- 验证数据库文件权限

## 🎯 最佳实践

1. **回测周期**: 建议至少 6 个月以上
2. **策略选择**: 根据风险偏好选择合适策略
3. **信号记录**: 定期保存信号以便分析
4. **性能监控**: 定期查看策略表现统计
5. **参数调整**: 根据回测结果优化策略参数

## 🔮 未来计划

- [ ] 支持更多技术指标
- [ ] 添加机器学习策略
- [ ] 实时信号推送
- [ ] 移动端适配
- [ ] 多账户管理

## 📞 支持

如有问题或建议：
- 查看文档: [DY_BACKTEST_GUIDE.md](DY_BACKTEST_GUIDE.md)
- 运行测试: `python test_dy_backtest.py`
- 查看示例: `python dy_backtest_example.py`

## 📄 许可证

MIT License

---

**版本**: v2.0
**更新时间**: 2026-03-04
**作者**: DY 量化团队

🎉 **立即开始使用！**

```bash
python dy_backtest_example.py
```
