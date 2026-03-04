#!/usr/bin/env python3
"""
DY 选股器测试脚本
使用少量股票快速测试功能
"""

from utils.dy_screener import DYScreener

# 测试股票列表（包含不同市值和流动性的股票）
test_symbols = [
    # 大盘股
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA',
    # 中盘股
    'COIN', 'MARA', 'RIOT', 'HOOD', 'SOFI', 'RBLX',
    # 小盘股
    'IREN', 'CLSK', 'CIFR', 'RGTI', 'QUBT',
    # ETF
    'SPY', 'QQQ', 'UVXY'
]

print("=" * 60)
print("DY 选股器测试")
print("=" * 60)
print(f"测试股票数量: {len(test_symbols)}")
print(f"测试股票列表: {', '.join(test_symbols)}")
print("=" * 60)

# 创建选股器（使用较低的过滤条件以便测试）
screener = DYScreener(
    min_price=0.1,
    min_volume_usd=1_000_000  # 降低到 100 万以便测试更多股票
)

# 筛选股票
results = screener.screen_stocks(test_symbols, max_workers=5)

# 显示结果
if not results.empty:
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)
    print(f"成功分析 {len(results)} 只股票\n")

    # 显示所有结果
    print("所有股票信号:")
    print("-" * 60)
    for _, row in results.iterrows():
        signals = []
        if row['buy']:
            signals.append('🟢BUY')
        if row['sell']:
            signals.append('🔴SELL')
        if row['up1']:
            signals.append('UP1')
        if row['up2']:
            signals.append('UP2')
        if row['up3']:
            signals.append('UP3')
        if row['down1']:
            signals.append('DN1')
        if row['down2']:
            signals.append('DN2')
        if row['down3']:
            signals.append('DN3')

        signal_str = ', '.join(signals) if signals else '-'
        print(f"{row['symbol']:8s} ${row['price']:8.2f}  {signal_str}")

    # 统计
    print(f"\n📊 信号统计:")
    print("-" * 60)
    print(f"买入信号:  {results['buy'].sum()} 只")
    print(f"卖出信号:  {results['sell'].sum()} 只")
    print(f"UP1:       {results['up1'].sum()} 只")
    print(f"UP2:       {results['up2'].sum()} 只")
    print(f"UP3:       {results['up3'].sum()} 只")
    print(f"DOWN1:     {results['down1'].sum()} 只")
    print(f"DOWN2:     {results['down2'].sum()} 只")
    print(f"DOWN3:     {results['down3'].sum()} 只")

    # 保存测试结果
    results.to_csv('test_results.csv', index=False)
    print(f"\n✅ 测试结果已保存到: test_results.csv")
    print("=" * 60)
else:
    print("\n❌ 测试失败：未能分析任何股票")

print("\n测试完成！如果结果正常，可以运行完整版本：")
print("python dy_stock_screener.py")
