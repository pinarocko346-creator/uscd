#!/usr/bin/env python3
"""
DY策略选股器 - 主程序
支持命令行参数和多线程处理
"""

import argparse
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from utils.dy_screener import DYScreener


def screen_single_stock(screener, symbol):
    """筛选单只股票（用于多线程）"""
    return screener.screen_stock(symbol)


def main():
    parser = argparse.ArgumentParser(description='DY策略美股选股器')
    parser.add_argument('--max-stocks', type=int, help='最大筛选股票数（测试用）')
    parser.add_argument('--workers', type=int, default=10, help='并发线程数（默认10）')
    parser.add_argument('--output', type=str, help='输出文件名')
    args = parser.parse_args()
    
    print("=" * 80)
    print("DY策略美股选股器")
    print("=" * 80)
    print("筛选条件：")
    print("  1. 价格 >= $0.10")
    print("  2. 日成交额 >= $10,000,000")
    print("  3. 有买卖或趋势信号")
    print("=" * 80)
    
    screener = DYScreener()
    
    # 获取股票列表
    print("\n正在获取股票列表...")
    symbols = screener.get_market_symbols()
    print(f"✓ 共获取 {len(symbols)} 只美股（S&P 500 + NASDAQ 100）")
    
    if args.max_stocks:
        symbols = symbols[:args.max_stocks]
        print(f"\n[测试模式] 只筛选前 {args.max_stocks} 只股票...")
    else:
        print(f"\n共 {len(symbols)} 只股票，开始筛选...")
    
    # 多线程筛选
    qualified_stocks = []
    total = len(symbols)
    processed = 0
    
    print(f"\n使用 {args.workers} 个线程并发处理...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_symbol = {executor.submit(screen_single_stock, screener, symbol): symbol 
                           for symbol in symbols}
        
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            processed += 1
            
            try:
                ok, info = future.result()
                if ok:
                    qualified_stocks.append(info)
                    signals = []
                    if info['buy']: signals.append('BUY')
                    if info['sell']: signals.append('SELL')
                    if info['up1']: signals.append('UP1')
                    if info['up2']: signals.append('UP2')
                    if info['up3']: signals.append('UP3')
                    if info['down1']: signals.append('DOWN1')
                    if info['down2']: signals.append('DOWN2')
                    if info['down3']: signals.append('DOWN3')
                    print(f"✓ [{processed}/{total}] {symbol} - {', '.join(signals)}")
            except Exception as e:
                pass
            
            if processed % 50 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed
                remaining = (total - processed) / rate
                print(f"进度: {processed}/{total} ({processed/total*100:.1f}%) - "
                      f"已选入 {len(qualified_stocks)} 只 - "
                      f"预计剩余 {remaining/60:.1f} 分钟")
    
    elapsed = time.time() - start_time
    
    print(f"\n{'=' * 80}")
    print(f"筛选完成，共 {len(qualified_stocks)} 只入选")
    print(f"总耗时: {elapsed/60:.1f} 分钟")
    print("=" * 80)
    
    if not qualified_stocks:
        print("当前无符合条件的股票。")
        return
    
    # 保存结果
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = args.output if args.output else f"dy_qualified_{ts}.csv"
    
    df = pd.DataFrame(qualified_stocks)
    df = df.sort_values('volume_usd', ascending=False)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n结果已保存: {output_file}")
    print(f"共 {len(qualified_stocks)} 只股票入选")
    
    # 统计信号
    buy_count = df['buy'].sum()
    sell_count = df['sell'].sum()
    up_count = (df['up1'] | df['up2'] | df['up3']).sum()
    down_count = (df['down1'] | df['down2'] | df['down3']).sum()
    
    print(f"\n信号统计：")
    if buy_count > 0:
        print(f"  BUY信号: {buy_count} 只")
    if sell_count > 0:
        print(f"  SELL信号: {sell_count} 只")
    if up_count > 0:
        print(f"  上涨趋势: {up_count} 只")
    if down_count > 0:
        print(f"  下跌趋势: {down_count} 只")


if __name__ == "__main__":
    main()
