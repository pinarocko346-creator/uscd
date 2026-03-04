#!/usr/bin/env python3
"""
DY 回测系统测试脚本
测试所有新增功能
"""

from utils.dy_backtest import BacktestEngine
from utils.dy_strategy_manager import StrategyManager
from utils.dy_signal_tracker import SignalTracker
from utils.dy_performance import PerformanceAnalyzer
from utils.dy_comparator import StrategyComparator
from datetime import datetime, timedelta


def test_backtest():
    """测试回测功能"""
    print("\n" + "=" * 60)
    print("测试 1: 策略回测")
    print("=" * 60)

    engine = BacktestEngine(initial_capital=100000)

    result = engine.backtest_single_stock(
        symbol='AAPL',
        start_date='2023-01-01',
        end_date='2024-01-01',
        strategy='stable'
    )

    if result:
        print(f"✅ 回测成功")
        print(f"   股票: {result['symbol']}")
        print(f"   总收益率: {result['total_return_pct']:.2f}%")
        print(f"   最大回撤: {result['max_drawdown_pct']:.2f}%")
        print(f"   胜率: {result['win_rate_pct']:.2f}%")
        print(f"   交易次数: {result['total_trades']}")
        return result
    else:
        print("❌ 回测失败")
        return None


def test_performance_analysis(backtest_result):
    """测试性能分析"""
    print("\n" + "=" * 60)
    print("测试 2: 性能分析")
    print("=" * 60)

    if not backtest_result:
        print("❌ 跳过（需要回测结果）")
        return

    analyzer = PerformanceAnalyzer()
    metrics = analyzer.calculate_metrics(backtest_result)

    print(f"✅ 性能指标计算成功")
    print(f"   夏普比率: {metrics['sharpe_ratio']:.2f}")
    print(f"   索提诺比率: {metrics['sortino_ratio']:.2f}")
    print(f"   卡玛比率: {metrics['calmar_ratio']:.2f}")
    print(f"   盈亏比: {metrics['profit_factor']:.2f}")

    # 生成图表
    try:
        equity_chart = analyzer.plot_equity_curve(backtest_result, 'test_equity.png')
        print(f"✅ 资金曲线图已生成: {equity_chart}")

        trade_chart = analyzer.plot_trade_analysis(backtest_result, 'test_trades.png')
        if trade_chart:
            print(f"✅ 交易分析图已生成: {trade_chart}")

        report_path = analyzer.generate_report(backtest_result, metrics, 'test_report.html')
        print(f"✅ HTML 报告已生成: {report_path}")
    except Exception as e:
        print(f"⚠️  图表生成失败: {e}")


def test_strategy_comparison():
    """测试策略对比"""
    print("\n" + "=" * 60)
    print("测试 3: 策略对比")
    print("=" * 60)

    comparator = StrategyComparator(initial_capital=100000)

    comparison = comparator.compare_strategies_single_stock(
        symbol='AAPL',
        start_date='2023-01-01',
        end_date='2024-01-01',
        strategies=['buy_signal', 'stable', 'strongest']
    )

    if not comparison.empty:
        print(f"✅ 策略对比成功")
        print("\n对比结果:")
        print(comparison[['strategy', 'total_return_pct', 'win_rate_pct', 'max_drawdown_pct']].to_string(index=False))

        # 排名
        ranked = comparator.rank_strategies(comparison)
        best = ranked.iloc[0]
        print(f"\n🏆 最佳策略: {best['strategy']} (得分: {best['score']:.2f})")
    else:
        print("❌ 策略对比失败")


def test_signal_tracker():
    """测试信号追踪"""
    print("\n" + "=" * 60)
    print("测试 4: 信号追踪")
    print("=" * 60)

    tracker = SignalTracker()

    # 保存测试信号
    test_signals = [
        {
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
        },
        {
            'date': '2024-01-16',
            'symbol': 'MSFT',
            'price': 375.20,
            'buy': True,
            'sell': False,
            'up1': True,
            'up2': True,
            'up3': False,
            'down1': False,
            'down2': False,
            'down3': False
        }
    ]

    count = tracker.save_signals_batch(test_signals)
    print(f"✅ 已保存 {count} 条信号")

    # 查询信号
    signals = tracker.get_signals(signal_type='buy')
    print(f"✅ 查询到 {len(signals)} 条买入信号")

    # 获取统计
    stats = tracker.get_signal_statistics(days=30)
    print(f"✅ 统计信息:")
    print(f"   总信号数: {stats['total_signals']}")
    print(f"   买入信号: {stats['buy_signals']}")
    print(f"   卖出信号: {stats['sell_signals']}")


def test_strategy_manager():
    """测试策略管理"""
    print("\n" + "=" * 60)
    print("测试 5: 策略管理")
    print("=" * 60)

    manager = StrategyManager()

    # 列出预定义策略
    strategies = manager.list_strategies()
    print(f"✅ 找到 {len(strategies)} 个策略")

    for strategy in strategies[:4]:  # 只显示前 4 个
        print(f"   - {strategy['name']}: {strategy['description']}")

    # 创建自定义策略
    custom = manager.create_custom_strategy(
        name='测试策略',
        description='买入 + UP1 + UP2',
        conditions={'buy': True, 'up1': True, 'up2': True},
        risk_level='low'
    )

    if manager.save_strategy('test_strategy', custom):
        print(f"✅ 自定义策略创建成功")
    else:
        print(f"❌ 自定义策略创建失败")

    # 创建组合
    portfolio = manager.create_portfolio(
        name='测试组合',
        strategies=[
            {'id': 'stable', 'weight': 0.6},
            {'id': 'strongest', 'weight': 0.4}
        ]
    )

    if manager.save_portfolio('test_portfolio', portfolio):
        print(f"✅ 策略组合创建成功")
    else:
        print(f"❌ 策略组合创建失败")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("DY 回测系统功能测试")
    print("=" * 60)
    print("开始测试所有功能...")

    try:
        # 测试 1: 回测
        backtest_result = test_backtest()

        # 测试 2: 性能分析
        test_performance_analysis(backtest_result)

        # 测试 3: 策略对比
        test_strategy_comparison()

        # 测试 4: 信号追踪
        test_signal_tracker()

        # 测试 5: 策略管理
        test_strategy_manager()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        print("\n提示:")
        print("1. 查看生成的图表: reports/ 目录")
        print("2. 查看 HTML 报告: reports/test_report.html")
        print("3. 启动 Web 服务: ./start_dy_web.sh")
        print("4. 访问回测页面: http://localhost:5001/backtest")

    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
