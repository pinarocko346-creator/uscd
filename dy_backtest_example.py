#!/usr/bin/env python3
"""
DY 回测系统快速示例
演示核心功能的使用
"""

print("=" * 60)
print("DY 策略回测系统 - 快速示例")
print("=" * 60)

# 示例 1: 简单回测
print("\n【示例 1】单股票回测")
print("-" * 60)

from utils.dy_backtest import BacktestEngine

engine = BacktestEngine(initial_capital=100000)

print("正在回测 AAPL (2023-01-01 到 2024-01-01)...")

result = engine.backtest_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategy='stable'
)

if result:
    print(f"\n✅ 回测完成！")
    print(f"   初始资金: ${result['initial_capital']:,.2f}")
    print(f"   最终资金: ${result['final_capital']:,.2f}")
    print(f"   总收益率: {result['total_return_pct']:.2f}%")
    print(f"   最大回撤: {result['max_drawdown_pct']:.2f}%")
    print(f"   胜率: {result['win_rate_pct']:.2f}%")
    print(f"   交易次数: {result['total_trades']}")
else:
    print("❌ 回测失败（可能是数据不足）")

# 示例 2: 策略对比
print("\n【示例 2】策略对比")
print("-" * 60)

from utils.dy_comparator import StrategyComparator

comparator = StrategyComparator()

print("正在对比三种策略...")

comparison = comparator.compare_strategies_single_stock(
    symbol='AAPL',
    start_date='2023-01-01',
    end_date='2024-01-01',
    strategies=['buy_signal', 'stable', 'strongest']
)

if not comparison.empty:
    print("\n✅ 对比完成！")
    print("\n策略对比结果:")
    print(comparison[['strategy', 'total_return_pct', 'win_rate_pct']].to_string(index=False))

    # 找出最佳策略
    ranked = comparator.rank_strategies(comparison)
    best = ranked.iloc[0]
    print(f"\n🏆 最佳策略: {best['strategy']}")
    print(f"   综合得分: {best['score']:.2f}")
    print(f"   总收益率: {best['total_return_pct']:.2f}%")
else:
    print("❌ 对比失败")

# 示例 3: 策略管理
print("\n【示例 3】策略管理")
print("-" * 60)

from utils.dy_strategy_manager import StrategyManager

manager = StrategyManager()

print("预定义策略列表:")
strategies = manager.list_strategies()

for i, strategy in enumerate(strategies[:4], 1):
    print(f"   {i}. {strategy['name']}")
    print(f"      {strategy['description']}")
    print(f"      风险等级: {strategy['risk_level']}")

# 创建自定义策略
print("\n创建自定义策略...")
custom = manager.create_custom_strategy(
    name='示例策略',
    description='买入信号 + UP1 突破',
    conditions={'buy': True, 'up1': True},
    risk_level='medium'
)

if manager.save_strategy('example_strategy', custom):
    print("✅ 自定义策略创建成功！")

# 示例 4: 信号追踪
print("\n【示例 4】信号追踪")
print("-" * 60)

from utils.dy_signal_tracker import SignalTracker
from datetime import datetime

tracker = SignalTracker()

# 保存示例信号
print("保存示例信号...")
test_signal = {
    'date': datetime.now().strftime('%Y-%m-%d'),
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

if tracker.save_signal(test_signal):
    print("✅ 信号保存成功！")

# 查询统计
print("\n查询最近 30 天统计...")
stats = tracker.get_signal_statistics(days=30)

print(f"   总信号数: {stats['total_signals']}")
print(f"   买入信号: {stats['buy_signals']}")
print(f"   卖出信号: {stats['sell_signals']}")
print(f"   UP1 信号: {stats['up1_signals']}")

# 总结
print("\n" + "=" * 60)
print("✅ 所有示例运行完成！")
print("=" * 60)

print("\n📚 下一步:")
print("   1. 查看完整文档: DY_BACKTEST_GUIDE.md")
print("   2. 运行完整测试: python test_dy_backtest.py")
print("   3. 启动 Web 服务: ./start_dy_web.sh")
print("   4. 访问回测页面: http://localhost:5001/backtest")

print("\n💡 提示:")
print("   - 回测需要网络连接（下载历史数据）")
print("   - 首次运行可能需要较长时间")
print("   - 生成的图表保存在 reports/ 目录")
print("   - 信号数据保存在 data/ 目录")
