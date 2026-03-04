#!/usr/bin/env python3
"""
测试 DY Web 服务是否正常工作
"""

import requests
import time

BASE_URL = 'http://localhost:5001'

def test_web_service():
    print("=" * 60)
    print("测试 DY Web 服务")
    print("=" * 60)

    # 测试 1: 检查主页
    print("\n1. 测试主页...")
    try:
        response = requests.get(f'{BASE_URL}/')
        if response.status_code == 200:
            print("✅ 主页正常")
        else:
            print(f"❌ 主页错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        print("请先启动 Web 服务: ./start_dy_web.sh")
        return False

    # 测试 2: 获取股票列表
    print("\n2. 测试获取股票列表...")
    try:
        response = requests.get(f'{BASE_URL}/api/stock_list')
        data = response.json()
        if data['success']:
            print(f"✅ 成功获取 {data['count']} 只股票")
        else:
            print(f"❌ 获取失败: {data.get('error')}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

    # 测试 3: 启动筛选（使用少量股票）
    print("\n3. 测试启动筛选...")
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    try:
        response = requests.post(
            f'{BASE_URL}/api/start_screening',
            json={
                'symbols': test_symbols,
                'min_price': 0.1,
                'min_volume': 1000000,
                'max_workers': 3
            }
        )
        data = response.json()
        if data['success']:
            print(f"✅ 筛选任务已启动，共 {data['total']} 只股票")

            # 等待完成
            print("\n等待筛选完成...")
            for i in range(30):  # 最多等待 30 秒
                time.sleep(1)
                status_response = requests.get(f'{BASE_URL}/api/status')
                status = status_response.json()

                if not status['running']:
                    print(f"✅ 筛选完成，找到 {status['result_count']} 只符合条件的股票")
                    break

                print(f"进度: {status['progress']}/{status['total']} - {status['current_step']}")
            else:
                print("⚠️  等待超时")

        else:
            print(f"❌ 启动失败: {data.get('error')}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

    # 测试 4: 获取结果
    print("\n4. 测试获取结果...")
    try:
        response = requests.get(f'{BASE_URL}/api/results')
        data = response.json()
        if data['success']:
            print(f"✅ 成功获取 {data['count']} 条结果")
            if data['count'] > 0:
                print("\n示例结果:")
                for result in data['results'][:3]:
                    signals = []
                    if result['buy']:
                        signals.append('BUY')
                    if result['sell']:
                        signals.append('SELL')
                    print(f"  {result['symbol']}: ${result['price']:.2f} - {', '.join(signals) if signals else '无信号'}")
        else:
            print(f"❌ 获取失败: {data.get('error')}")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n访问 http://localhost:5001 查看完整界面")

    return True


if __name__ == '__main__':
    test_web_service()
