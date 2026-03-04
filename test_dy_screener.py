#!/usr/bin/env python3
"""
DY策略选股器 - 快速测试脚本
测试前10只股票，快速验证功能
"""

from utils.dy_screener import DYScreener
import time


def main():
    print("=" * 60)
    print("DY策略选股器 - 快速测试")
    print("=" * 60)
    
    screener = DYScreener()
    
    # 测试股票列表
    test_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'META', 'TSLA', 'AMD', 'NFLX', 'INTC'
    ]
    
    print(f"\n测试 {len(test_symbols)} 只股票...")
    print("-" * 60)
    
    qualified = []
    start_time = time.time()
    
    for i, symbol in enumerate(test_symbols, 1):
        print(f"\n[{i}/{len(test_symbols)}] 正在分析 {symbol}...")
        
        ok, info = screener.screen_stock(symbol)
        
        if ok:
            qualified.append(info)
            signals = []
            if info['buy']: signals.append('BUY')
            if info['sell']: signals.append('SELL')
            if info['up1']: signals.append('UP1')
            if info['up2']: signals.append('UP2')
            if info['up3']: signals.append('UP3')
            if info['down1']: signals.append('DOWN1')
            if info['down2']: signals.append('DOWN2')
            if info['down3']: signals.append('DOWN3')
            
            print(f"  ✓ 有信号: {', '.join(signals)}")
            print(f"  价格: ${info['price']:.2f}")
            print(f"  成交额: ${info['volume_usd']:.2f}M")
            print(f"  DIFF: {info['diff']:.4f}, DEA: {info['dea']:.4f}")
        else:
            print(f"  ✗ 无信号或不符合条件")
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"测试完成！")
    print(f"入选: {len(qualified)}/{len(test_symbols)} 只")
    print(f"耗时: {elapsed:.2f} 秒")
    print("=" * 60)
    
    if qualified:
        print("\n入选股票：")
        for stock in qualified:
            signals = []
            if stock['buy']: signals.append('BUY')
            if stock['sell']: signals.append('SELL')
            if stock['up1']: signals.append('UP1')
            if stock['up2']: signals.append('UP2')
            if stock['up3']: signals.append('UP3')
            if stock['down1']: signals.append('DOWN1')
            if stock['down2']: signals.append('DOWN2')
            if stock['down3']: signals.append('DOWN3')
            print(f"  {stock['symbol']}: {', '.join(signals)}")
    
    print("\n✓ 测试通过！可以运行完整版：")
    print("  python dy_stock_screener.py")


if __name__ == "__main__":
    main()
