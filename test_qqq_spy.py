#!/usr/bin/env python3
"""测试QQQ和SPY的DY策略信号"""

from utils.dy_screener import DYScreener

def main():
    screener = DYScreener()
    
    for symbol in ['QQQ', 'SPY']:
        print(f'\n{"="*60}')
        print(f'分析 {symbol} (日线数据)')
        print("="*60)
        
        passed, result = screener.screen_stock(symbol)
        
        if not passed:
            print(f'✗ {symbol}: 无信号或不符合条件')
            continue
        
        # 显示结果
        print(f'价格: ${result["price"]:.2f}')
        print(f'成交额: ${result["volume_usd"]:.2f}M')
        print(f'\nMACD:')
        print(f'  DIFF: {result["diff"]:.4f}')
        print(f'  DEA: {result["dea"]:.4f}')
        print(f'\n信号:')
        print(f'  BUY: {result["buy"]}')
        print(f'  SELL: {result["sell"]}')
        print(f'  UP1: {result["up1"]}  UP2: {result["up2"]}  UP3: {result["up3"]}')
        print(f'  DOWN1: {result["down1"]}  DOWN2: {result["down2"]}  DOWN3: {result["down3"]}')
        
        # 判断类别
        if result['buy']:
            if result['up3']:
                print(f'\n🚀 【最强策略】买入信号 + UP3')
            elif result['up1']:
                print(f'\n📈 【稳健策略】买入信号 + UP1')
            else:
                print(f'\n💰 【激进策略】买入信号')
        elif result['sell']:
            print(f'\n⚠️  【风险控制】卖出信号')
        elif result['down1'] or result['down2'] or result['down3']:
            downs = []
            if result['down1']: downs.append('DOWN1')
            if result['down2']: downs.append('DOWN2')
            if result['down3']: downs.append('DOWN3')
            print(f'\n📉 【风险信号】{" + ".join(downs)}')
        else:
            print(f'\n⚪ 无明确信号')

if __name__ == '__main__':
    main()
