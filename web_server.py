"""
Web服务器 - 提供前端界面和API
"""
from flask import Flask, render_template, jsonify, request
import sys
import os
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from layer1_cornerstone import Layer1Strategy
from layer2_rotation import Layer2Strategy
from layer3_timing import Layer3Strategy
from utils import PerformanceMetrics
from config import TOTAL_CAPITAL, LAYER1_WEIGHT, LAYER2_WEIGHT, LAYER3_WEIGHT

app = Flask(__name__)

# 全局策略实例
layer1 = Layer1Strategy()
layer2 = Layer2Strategy()
layer3 = Layer3Strategy()

# 存储运行历史
run_history = []


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_capital': TOTAL_CAPITAL,
        'layers': {
            'layer1': {
                'name': '基石层',
                'weight': LAYER1_WEIGHT,
                'capital': TOTAL_CAPITAL * LAYER1_WEIGHT,
                'holdings_count': len(layer1.current_holdings)
            },
            'layer2': {
                'name': '轮动层',
                'weight': LAYER2_WEIGHT,
                'capital': TOTAL_CAPITAL * LAYER2_WEIGHT,
                'holdings_count': len(layer2.current_holdings)
            },
            'layer3': {
                'name': '择时层',
                'weight': LAYER3_WEIGHT,
                'capital': TOTAL_CAPITAL * LAYER3_WEIGHT,
                'position': layer3.current_position
            }
        }
    })


@app.route('/api/holdings')
def get_holdings():
    """获取持仓信息"""
    holdings = {
        'layer1': [
            {'code': code, 'weight': weight * 100}
            for code, weight in layer1.current_holdings.items()
        ],
        'layer2': [
            {'code': code, 'weight': weight * 100}
            for code, weight in layer2.current_holdings.items()
        ],
        'layer3': {
            'position': layer3.current_position * 100
        }
    }
    return jsonify(holdings)


@app.route('/api/run', methods=['POST'])
def run_system():
    """运行系统"""
    try:
        date = request.json.get('date') or datetime.now().strftime('%Y-%m-%d')

        # 运行三层策略
        result1 = layer1.run(date)
        result2 = layer2.run(date)
        result3 = layer3.run(date)

        # 记录历史
        run_record = {
            'date': date,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'layer1': result1.get('success'),
            'layer2': result2.get('success'),
            'layer3': result3.get('success')
        }
        run_history.append(run_record)

        return jsonify({
            'success': True,
            'message': '系统运行完成',
            'results': {
                'layer1': result1,
                'layer2': result2,
                'layer3': result3
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'运行失败: {str(e)}'
        }), 500


@app.route('/api/run_layer/<layer_name>', methods=['POST'])
def run_layer(layer_name):
    """运行单个层级"""
    try:
        date = request.json.get('date') or datetime.now().strftime('%Y-%m-%d')

        if layer_name == 'layer1':
            result = layer1.run(date)
        elif layer_name == 'layer2':
            result = layer2.run(date)
        elif layer_name == 'layer3':
            result = layer3.run(date)
        else:
            return jsonify({'success': False, 'message': '无效的层级名称'}), 400

        return jsonify({
            'success': True,
            'message': f'{layer_name}运行完成',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'运行失败: {str(e)}'
        }), 500


@app.route('/api/history')
def get_history():
    """获取运行历史"""
    return jsonify({
        'history': run_history[-50:]  # 最近50条记录
    })


@app.route('/api/performance')
def get_performance():
    """获取性能指标（模拟数据）"""
    import numpy as np

    # 生成模拟收益曲线
    dates = [(datetime.now().replace(day=1) + pd.Timedelta(days=i)).strftime('%Y-%m-%d')
             for i in range(0, 90, 3)]

    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, len(dates))
    cumulative = (1 + pd.Series(returns)).cumprod() - 1

    return jsonify({
        'dates': dates,
        'cumulative_returns': cumulative.tolist(),
        'metrics': {
            'total_return': cumulative.iloc[-1] * 100,
            'annual_return': 18.5,
            'sharpe_ratio': 1.65,
            'max_drawdown': -12.3,
            'win_rate': 62.5
        }
    })


@app.route('/api/config')
def get_config():
    """获取配置信息"""
    from config import (
        LAYER1_FACTOR_WEIGHTS,
        LAYER2_GOLDEN_FACTOR_COUNT,
        LAYER1_SINGLE_STOCK_STOP_LOSS,
        DATA_SOURCE
    )

    return jsonify({
        'system': {
            'total_capital': TOTAL_CAPITAL,
            'data_source': DATA_SOURCE
        },
        'layer1': {
            'weight': LAYER1_WEIGHT,
            'factor_weights': LAYER1_FACTOR_WEIGHTS,
            'stop_loss': LAYER1_SINGLE_STOCK_STOP_LOSS
        },
        'layer2': {
            'weight': LAYER2_WEIGHT,
            'golden_factor_count': LAYER2_GOLDEN_FACTOR_COUNT
        },
        'layer3': {
            'weight': LAYER3_WEIGHT
        }
    })


if __name__ == '__main__':
    import pandas as pd
    print("\n" + "="*80)
    print("三层量化系统 - Web界面")
    print("="*80)
    print("\n启动Web服务器...")
    print("访问地址: http://localhost:8080")
    print("或者: http://127.0.0.1:8080")
    print("\n按 Ctrl+C 停止服务器\n")
    print("="*80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=8080)
