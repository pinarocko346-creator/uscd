#!/usr/bin/env python3
"""
DY 选股器 Web 服务
提供前端界面和 API 接口
"""

from flask import Flask, render_template, jsonify, request, Response, send_file
from utils.dy_screener import DYScreener, get_us_stock_list
from utils.dy_strategy_manager import StrategyManager
from utils.dy_signal_tracker import SignalTracker
from utils.dy_backtest import BacktestEngine
from utils.dy_performance import PerformanceAnalyzer
from utils.dy_comparator import StrategyComparator
import json
import time
from threading import Thread, Lock
import queue
from datetime import datetime, timedelta
import os

app = Flask(__name__,
            template_folder='templates/dy',
            static_folder='static')

# 全局状态
screening_status = {
    'running': False,
    'progress': 0,
    'total': 0,
    'current_step': '',
    'results': [],
    'error': None
}
status_lock = Lock()
progress_queue = queue.Queue()

# 初始化管理器
strategy_manager = StrategyManager()
signal_tracker = SignalTracker()
backtest_engine = BacktestEngine()
performance_analyzer = PerformanceAnalyzer()
strategy_comparator = StrategyComparator()


def update_progress(step, current, total, message=''):
    """更新进度"""
    with status_lock:
        screening_status['current_step'] = step
        screening_status['progress'] = current
        screening_status['total'] = total

    # 发送到队列供 SSE 使用
    progress_data = {
        'step': step,
        'current': current,
        'total': total,
        'message': message,
        'percentage': int((current / total * 100)) if total > 0 else 0
    }
    progress_queue.put(progress_data)


def run_screening(symbols, min_price, min_volume, max_workers):
    """后台运行筛选任务"""
    try:
        with status_lock:
            screening_status['running'] = True
            screening_status['error'] = None
            screening_status['results'] = []

        update_progress('初始化', 0, len(symbols), '正在初始化选股器...')

        # 创建选股器
        screener = DYScreener(min_price=min_price, min_volume_usd=min_volume)

        # 自定义筛选逻辑，添加进度回调
        results = []

        # 第一步：过滤股票
        update_progress('过滤', 0, len(symbols), '正在应用价格和交易量过滤...')
        filtered_symbols = []

        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {executor.submit(screener.filter_stock, symbol): symbol
                              for symbol in symbols}
            for i, future in enumerate(as_completed(future_to_symbol), 1):
                try:
                    if future.result():
                        filtered_symbols.append(future_to_symbol[future])
                    update_progress('过滤', i, len(symbols),
                                  f'已过滤 {i}/{len(symbols)} 只股票，通过 {len(filtered_symbols)} 只')
                except Exception:
                    pass

        # 第二步：分析股票
        update_progress('分析', 0, len(filtered_symbols), '正在计算技术指标...')
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {executor.submit(screener.analyze_stock, symbol): symbol
                              for symbol in filtered_symbols}
            for i, future in enumerate(as_completed(future_to_symbol), 1):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    update_progress('分析', i, len(filtered_symbols),
                                  f'已分析 {i}/{len(filtered_symbols)} 只股票')
                except Exception:
                    pass

        # 完成
        with status_lock:
            screening_status['results'] = results
            screening_status['running'] = False

        update_progress('完成', len(results), len(results),
                       f'筛选完成！找到 {len(results)} 只符合条件的股票')

    except Exception as e:
        with status_lock:
            screening_status['running'] = False
            screening_status['error'] = str(e)
        update_progress('错误', 0, 0, f'发生错误: {str(e)}')


@app.route('/')
def index():
    """主页"""
    return render_template('dy_screener.html')


@app.route('/advanced')
def advanced():
    """高级功能页面"""
    return render_template('dy_advanced.html')


@app.route('/backtest')
def backtest_page():
    """回测分析页面"""
    return render_template('dy_backtest.html')


@app.route('/api/stock_list')
def get_stock_list():
    """获取股票列表"""
    try:
        symbols = get_us_stock_list()
        return jsonify({
            'success': True,
            'symbols': symbols,
            'count': len(symbols)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/start_screening', methods=['POST'])
def start_screening():
    """开始筛选"""
    with status_lock:
        if screening_status['running']:
            return jsonify({
                'success': False,
                'error': '筛选任务正在运行中'
            }), 400

    data = request.json
    symbols = data.get('symbols', [])
    min_price = float(data.get('min_price', 0.1))
    min_volume = float(data.get('min_volume', 10_000_000))
    max_workers = int(data.get('max_workers', 10))

    if not symbols:
        # 如果没有指定股票，自动获取
        symbols = get_us_stock_list()

    # 清空进度队列
    while not progress_queue.empty():
        try:
            progress_queue.get_nowait()
        except queue.Empty:
            break

    # 启动后台线程
    thread = Thread(target=run_screening,
                   args=(symbols, min_price, min_volume, max_workers))
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': '筛选任务已启动',
        'total': len(symbols)
    })


@app.route('/api/status')
def get_status():
    """获取当前状态"""
    with status_lock:
        return jsonify({
            'running': screening_status['running'],
            'progress': screening_status['progress'],
            'total': screening_status['total'],
            'current_step': screening_status['current_step'],
            'error': screening_status['error'],
            'result_count': len(screening_status['results'])
        })


@app.route('/api/results')
def get_results():
    """获取筛选结果"""
    with status_lock:
        results = screening_status['results'].copy()

    # 支持筛选
    signal_filter = request.args.get('filter', 'all')

    if signal_filter == 'buy':
        # 激进策略：只看买入信号
        results = [r for r in results if r['buy']]
    elif signal_filter == 'sell':
        # 风险控制：关注卖出信号
        results = [r for r in results if r['sell']]
    elif signal_filter == 'up':
        results = [r for r in results if r['up1'] or r['up2'] or r['up3']]
    elif signal_filter == 'down':
        results = [r for r in results if r['down1'] or r['down2'] or r['down3']]
    elif signal_filter == 'aggressive':
        # 激进策略：买入信号
        results = [r for r in results if r['buy']]
    elif signal_filter == 'stable':
        # 稳健策略：买入信号 + 上涨趋势（UP1）
        results = [r for r in results if r['buy'] and r['up1']]
    elif signal_filter == 'strongest':
        # 最强策略：买入信号 + 强势突破（UP3）
        results = [r for r in results if r['buy'] and r['up3']]
    elif signal_filter == 'risk_alert':
        # 风险警示：卖出信号
        results = [r for r in results if r['sell']]
    elif signal_filter == 'buy_up1':
        # 买入 + UP1
        results = [r for r in results if r['buy'] and r['up1']]
    elif signal_filter == 'buy_up2':
        # 买入 + UP2
        results = [r for r in results if r['buy'] and r['up2']]
    elif signal_filter == 'buy_up3':
        # 买入 + UP3
        results = [r for r in results if r['buy'] and r['up3']]
    elif signal_filter == 'buy_any_up':
        # 买入 + 任意上涨趋势
        results = [r for r in results if r['buy'] and (r['up1'] or r['up2'] or r['up3'])]
    elif signal_filter == 'sell_down':
        # 卖出 + 下跌趋势
        results = [r for r in results if r['sell'] and (r['down1'] or r['down2'] or r['down3'])]
    elif signal_filter == 'strong_up':
        # 强势上涨：UP2 + UP3
        results = [r for r in results if r['up2'] and r['up3']]
    elif signal_filter == 'weak_down':
        # 弱势下跌：DOWN2 + DOWN3
        results = [r for r in results if r['down2'] and r['down3']]

    return jsonify({
        'success': True,
        'results': results,
        'count': len(results)
    })


@app.route('/api/progress_stream')
def progress_stream():
    """SSE 进度流"""
    def generate():
        while True:
            try:
                # 等待新的进度更新
                progress = progress_queue.get(timeout=1)
                yield f"data: {json.dumps(progress)}\n\n"
            except queue.Empty:
                # 发送心跳
                yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

            # 检查是否完成
            with status_lock:
                if not screening_status['running'] and progress_queue.empty():
                    break

    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/export_csv')
def export_csv():
    """导出 CSV"""
    import pandas as pd
    from io import StringIO

    with status_lock:
        results = screening_status['results'].copy()

    if not results:
        return jsonify({
            'success': False,
            'error': '没有可导出的数据'
        }), 400

    df = pd.DataFrame(results)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    return Response(
        csv_buffer.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=dy_screener_results.csv'}
    )


# ========== 新增功能 API ==========

@app.route('/api/custom_strategies', methods=['GET'])
def get_custom_strategies():
    """获取自定义策略列表"""
    strategies = strategy_manager.list_strategies()
    return jsonify({
        'success': True,
        'strategies': strategies
    })


@app.route('/api/custom_strategies', methods=['POST'])
def create_custom_strategy():
    """创建自定义策略"""
    data = request.json
    strategy = CustomStrategy(
        name=data['name'],
        description=data['description'],
        conditions=data['conditions']
    )

    success = strategy_manager.add_strategy(strategy)
    return jsonify({
        'success': success,
        'message': '策略创建成功' if success else '策略名称已存在'
    })


@app.route('/api/custom_strategies/<name>', methods=['DELETE'])
def delete_custom_strategy(name):
    """删除自定义策略"""
    success = strategy_manager.delete_strategy(name)
    return jsonify({
        'success': success,
        'message': '策略删除成功' if success else '策略不存在'
    })


@app.route('/api/apply_custom_strategy/<name>')
def apply_custom_strategy(name):
    """应用自定义策略"""
    with status_lock:
        results = screening_status['results'].copy()

    filtered = strategy_manager.apply_strategy(name, results)

    return jsonify({
        'success': True,
        'results': filtered,
        'count': len(filtered)
    })


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """运行回测"""
    data = request.json
    symbol = data.get('symbol')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    strategy = data.get('strategy', 'stable')

    if not symbol or not start_date or not end_date:
        return jsonify({
            'success': False,
            'error': '缺少必要参数'
        }), 400

    try:
        result = backtest_engine.backtest_single_stock(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strategy=strategy
        )

        if not result:
            return jsonify({
                'success': False,
                'error': '回测失败，可能是数据不足'
            }), 400

        # 计算性能指标
        metrics = performance_analyzer.calculate_metrics(result)

        # 生成图表
        equity_chart = performance_analyzer.plot_equity_curve(result, f'equity_{symbol}_{strategy}.png')
        trade_chart = performance_analyzer.plot_trade_analysis(result, f'trades_{symbol}_{strategy}.png')

        return jsonify({
            'success': True,
            'result': {
                'symbol': result['symbol'],
                'strategy': strategy,
                'initial_capital': result['initial_capital'],
                'final_capital': result['final_capital'],
                'total_return_pct': metrics['total_return_pct'],
                'annual_return_pct': metrics['annual_return_pct'],
                'max_drawdown_pct': metrics['max_drawdown_pct'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'sortino_ratio': metrics['sortino_ratio'],
                'win_rate_pct': metrics['win_rate_pct'],
                'total_trades': metrics['total_trades'],
                'profit_factor': metrics['profit_factor'],
                'equity_chart': os.path.basename(equity_chart) if equity_chart else None,
                'trade_chart': os.path.basename(trade_chart) if trade_chart else None
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/compare_strategies', methods=['POST'])
def compare_strategies_api():
    """对比多个策略"""
    data = request.json
    symbol = data.get('symbol')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    strategies = data.get('strategies', ['buy_signal', 'stable', 'strongest'])

    if not symbol or not start_date or not end_date:
        return jsonify({
            'success': False,
            'error': '缺少必要参数'
        }), 400

    try:
        comparison_df = strategy_comparator.compare_strategies_single_stock(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            strategies=strategies
        )

        if comparison_df.empty:
            return jsonify({
                'success': False,
                'error': '对比失败，可能是数据不足'
            }), 400

        # 生成对比图表
        chart_path = performance_analyzer.plot_strategy_comparison(
            comparison_df,
            f'comparison_{symbol}.png'
        )

        # 生成排名
        ranked_df = strategy_comparator.rank_strategies(comparison_df)

        return jsonify({
            'success': True,
            'comparison': comparison_df.to_dict('records'),
            'ranking': ranked_df[['strategy', 'score', 'rank']].to_dict('records'),
            'chart': os.path.basename(chart_path) if chart_path else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/save_signals', methods=['POST'])
def save_signals():
    """保存今日信号"""
    data = request.json
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

    with status_lock:
        results = screening_status['results'].copy()

    if not results:
        return jsonify({
            'success': False,
            'error': '没有可保存的信号'
        }), 400

    # 保存信号
    count = 0
    for result in results:
        signal = {
            'date': date,
            'symbol': result['symbol'],
            'price': result['price'],
            'buy': result.get('buy', False),
            'sell': result.get('sell', False),
            'up1': result.get('up1', False),
            'up2': result.get('up2', False),
            'up3': result.get('up3', False),
            'down1': result.get('down1', False),
            'down2': result.get('down2', False),
            'down3': result.get('down3', False)
        }
        if signal_tracker.save_signal(signal):
            count += 1

    return jsonify({
        'success': True,
        'message': f'已保存 {count} 条信号记录'
    })


@app.route('/api/signal_history')
def get_signal_history():
    """获取历史信号"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    symbol = request.args.get('symbol')
    signal_type = request.args.get('signal_type')

    df = signal_tracker.get_signals(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        signal_type=signal_type
    )

    return jsonify({
        'success': True,
        'signals': df.to_dict('records'),
        'count': len(df)
    })


@app.route('/api/signal_statistics')
def get_signal_statistics():
    """获取信号统计"""
    symbol = request.args.get('symbol')
    signal_type = request.args.get('signal_type')
    days = int(request.args.get('days', 30))

    stats = signal_tracker.get_signal_statistics(
        symbol=symbol,
        signal_type=signal_type,
        days=days
    )

    return jsonify({
        'success': True,
        'statistics': stats
    })


@app.route('/api/strategies')
def list_strategies():
    """列出所有策略"""
    strategies = strategy_manager.list_strategies()

    return jsonify({
        'success': True,
        'strategies': strategies
    })


@app.route('/api/strategy', methods=['POST'])
def create_strategy():
    """创建自定义策略"""
    data = request.json
    name = data.get('name')
    description = data.get('description')
    conditions = data.get('conditions')

    if not name or not conditions:
        return jsonify({
            'success': False,
            'error': '缺少必要参数'
        }), 400

    strategy = strategy_manager.create_custom_strategy(
        name=name,
        description=description,
        conditions=conditions,
        risk_level=data.get('risk_level', 'medium'),
        expected_return=data.get('expected_return', ''),
        holding_period=data.get('holding_period', '')
    )

    strategy_id = data.get('id', name.lower().replace(' ', '_'))
    if strategy_manager.save_strategy(strategy_id, strategy):
        return jsonify({
            'success': True,
            'strategy_id': strategy_id,
            'message': '策略创建成功'
        })
    else:
        return jsonify({
            'success': False,
            'error': '策略保存失败'
        }), 500


@app.route('/api/strategy/<strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    """删除策略"""
    if strategy_manager.delete_strategy(strategy_id):
        return jsonify({
            'success': True,
            'message': '策略删除成功'
        })
    else:
        return jsonify({
            'success': False,
            'error': '策略删除失败'
        }), 500


@app.route('/api/reports/<filename>')
def get_report(filename):
    """获取报告文件"""
    filepath = os.path.join(performance_analyzer.output_dir, filename)
    if os.path.exists(filepath):
        return send_file(filepath)
    else:
        return jsonify({
            'success': False,
            'error': '文件不存在'
        }), 404


if __name__ == '__main__':
    print("=" * 60)
    print("DY 选股器 Web 服务")
    print("=" * 60)
    print("访问地址: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
