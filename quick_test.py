#!/usr/bin/env python3
"""快速测试 - 生成示例数据"""

print('=' * 60)
print('快速测试 - 生成示例数据')
print('=' * 60)

# 测试 1: 简单回测
print('\n【测试 1】回测 AAPL...')
from utils.dy_backtest import BacktestEngine

engine = BacktestEngine(initial_capital=100000)
result = engine.backtest_single_stock(
    symbol='AAPL',
    start_date='2024-01-01',
    end_date='2024-03-01',
    strategy='stable'
)

if result:
    print(f'✅ 回测成功！')
    print(f'   总收益率: {result["total_return_pct"]:.2f}%')
    print(f'   交易次数: {result["total_trades"]}')
else:
    print('❌ 回测失败')

# 测试 2: 保存信号
print('\n【测试 2】保存测试信号...')
from utils.dy_signal_tracker import SignalTracker
from datetime import datetime

tracker = SignalTracker()
test_signals = [
    {
        'date': '2024-03-01',
        'symbol': 'AAPL',
        'price': 180.75,
        'buy': True,
        'sell': False,
        'up1': True,
        'up2': False,
        'up3': False,
        'down1': False,
        'down2': False,
        'down3': False
    },
    {
        'date': '2024-03-01',
        'symbol': 'MSFT',
        'price': 420.50,
        'buy': True,
        'sell': False,
        'up1': True,
        'up2': True,
        'up3': False,
        'down1': False,
        'down2': False,
        'down3': False
    },
    {
        'date': '2024-03-02',
        'symbol': 'GOOGL',
        'price': 140.25,
        'buy': False,
        'sell': True,
        'up1': False,
        'up2': False,
        'up3': False,
        'down1': True,
        'down2': False,
        'down3': False
    }
]

count = tracker.save_signals_batch(test_signals)
print(f'✅ 已保存 {count} 条信号')

# 测试 3: 查询统计
print('\n【测试 3】查询统计...')
stats = tracker.get_signal_statistics(days=30)
print(f'✅ 统计完成')
print(f'   总信号数: {stats["total_signals"]}')
print(f'   买入信号: {stats["buy_signals"]}')
print(f'   卖出信号: {stats["sell_signals"]}')

print('\n' + '=' * 60)
print('✅ 测试完成！')
print('=' * 60)
print('\n现在可以：')
print('1. 访问 http://localhost:5001/backtest')
print('2. 点击"信号追踪"标签查看统计数据')
print('3. 或者在"策略回测"中输入 AAPL 进行回测')
