#!/usr/bin/env python3
"""
DY 选股器主程序
基于 TradingView Pine Script 的 DY 指标实现美股选股
"""

import argparse
from utils.dy_screener import DYScreener, get_us_stock_list
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description='DY 指标美股选股器')
    parser.add_argument('--min-price', type=float, default=0.1,
                        help='最低股价（美元），默认 0.1')
    parser.add_argument('--min-volume', type=float, default=10_000_000,
                        help='最低交易额（美元），默认 10,000,000')
    parser.add_argument('--workers', type=int, default=10,
                        help='并发线程数，默认 10')
    parser.add_argument('--symbols', type=str, nargs='+',
                        help='指定股票代码列表，不指定则自动获取市场股票')
    parser.add_argument('--output', type=str, default='dy_screener_results.csv',
                        help='输出文件名，默认 dy_screener_results.csv')

    args = parser.parse_args()

    print("=" * 60)
    print("DY 指标美股选股器")
    print("=" * 60)
    print(f"筛选条件:")
    print(f"  - 最低股价: ${args.min_price}")
    print(f"  - 最低交易额: ${args.min_volume:,.0f}")
    print(f"  - 并发线程: {args.workers}")
    print("=" * 60)

    # 创建选股器
    screener = DYScreener(
        min_price=args.min_price,
        min_volume_usd=args.min_volume
    )

    # 获取股票列表
    if args.symbols:
        symbols = args.symbols
        print(f"\n使用指定的 {len(symbols)} 只股票")
    else:
        symbols = get_us_stock_list()
        print(f"\n自动获取到 {len(symbols)} 只股票")

    # 筛选股票
    results = screener.screen_stocks(symbols, max_workers=args.workers)

    # 显示和保存结果
    if not results.empty:
        print("\n" + "=" * 60)
        print("筛选结果")
        print("=" * 60)
        print(f"总共找到 {len(results)} 只符合条件的股票\n")

        # 显示买入信号的股票
        buy_signals = results[results['buy'] == True]
        if not buy_signals.empty:
            print(f"\n🟢 买入信号 ({len(buy_signals)} 只):")
            print("-" * 60)
            for _, row in buy_signals.iterrows():
                signals = []
                if row['up1']:
                    signals.append('UP1(突破蓝带)')
                if row['up2']:
                    signals.append('UP2(突破黄带)')
                if row['up3']:
                    signals.append('UP3(蓝带>黄带)')
                print(f"{row['symbol']:8s} ${row['price']:8.2f}  {', '.join(signals)}")

        # 显示卖出信号的股票
        sell_signals = results[results['sell'] == True]
        if not sell_signals.empty:
            print(f"\n🔴 卖出信号 ({len(sell_signals)} 只):")
            print("-" * 60)
            for _, row in sell_signals.iterrows():
                signals = []
                if row['down1']:
                    signals.append('DOWN1(跌破蓝带)')
                if row['down2']:
                    signals.append('DOWN2(跌破黄带)')
                if row['down3']:
                    signals.append('DOWN3(蓝带<黄带)')
                print(f"{row['symbol']:8s} ${row['price']:8.2f}  {', '.join(signals)}")

        # 显示趋势信号统计
        print(f"\n📊 趋势信号统计:")
        print("-" * 60)
        print(f"UP1 (突破蓝带上轨):     {results['up1'].sum()} 只")
        print(f"UP2 (突破黄带上轨):     {results['up2'].sum()} 只")
        print(f"UP3 (蓝带突破黄带):     {results['up3'].sum()} 只")
        print(f"DOWN1 (跌破蓝带下轨):   {results['down1'].sum()} 只")
        print(f"DOWN2 (跌破黄带下轨):   {results['down2'].sum()} 只")
        print(f"DOWN3 (蓝带跌破黄带):   {results['down3'].sum()} 只")

        # 保存完整结果
        results.to_csv(args.output, index=False)
        print(f"\n✅ 完整结果已保存到: {args.output}")
        print("=" * 60)
    else:
        print("\n❌ 未找到符合条件的股票")


if __name__ == '__main__':
    main()
