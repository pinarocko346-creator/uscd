"""
DY 性能统计和图表生成
生成策略性能报告和可视化图表
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os


class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self, output_dir: str = 'reports'):
        """
        初始化性能分析器

        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 设置绘图样式
        sns.set_style('whitegrid')
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False

    def calculate_metrics(self, backtest_result: Dict) -> Dict:
        """
        计算性能指标

        Args:
            backtest_result: 回测结果

        Returns:
            性能指标字典
        """
        equity_curve = pd.DataFrame(backtest_result['equity_curve'])

        # 基础指标
        total_return = backtest_result['total_return']
        total_return_pct = backtest_result['total_return_pct']
        max_drawdown = backtest_result['max_drawdown']
        max_drawdown_pct = backtest_result['max_drawdown_pct']

        # 计算年化收益率
        days = len(equity_curve)
        years = days / 252  # 交易日
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        # 计算夏普比率
        equity_series = equity_curve['equity']
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(252)) if len(returns) > 0 and returns.std() > 0 else 0

        # 计算索提诺比率（只考虑下行波动）
        downside_returns = returns[returns < 0]
        sortino_ratio = (returns.mean() / downside_returns.std() * np.sqrt(252)) if len(downside_returns) > 0 and downside_returns.std() > 0 else 0

        # 计算卡玛比率
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

        # 计算最大连续盈利/亏损
        trades = backtest_result['trades']
        consecutive_wins = 0
        consecutive_losses = 0
        max_consecutive_wins = 0
        max_consecutive_losses = 0

        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                profit = sell_trade['proceeds'] - buy_trade['cost']

                if profit > 0:
                    consecutive_wins += 1
                    consecutive_losses = 0
                    max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
                else:
                    consecutive_losses += 1
                    consecutive_wins = 0
                    max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)

        # 计算平均盈利/亏损
        profits = []
        losses = []

        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                profit = sell_trade['proceeds'] - buy_trade['cost']

                if profit > 0:
                    profits.append(profit)
                else:
                    losses.append(abs(profit))

        avg_profit = np.mean(profits) if profits else 0
        avg_loss = np.mean(losses) if losses else 0
        profit_factor = sum(profits) / sum(losses) if losses and sum(losses) > 0 else 0

        return {
            'total_return_pct': total_return_pct,
            'annual_return_pct': annual_return * 100,
            'max_drawdown_pct': max_drawdown_pct,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'win_rate_pct': backtest_result['win_rate_pct'],
            'total_trades': backtest_result['total_trades'],
            'winning_trades': backtest_result['winning_trades'],
            'losing_trades': backtest_result['total_trades'] - backtest_result['winning_trades'],
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor
        }

    def plot_equity_curve(self, backtest_result: Dict, filename: str = 'equity_curve.png'):
        """
        绘制资金曲线

        Args:
            backtest_result: 回测结果
            filename: 输出文件名
        """
        equity_curve = pd.DataFrame(backtest_result['equity_curve'])

        plt.figure(figsize=(14, 7))

        # 绘制资金曲线
        plt.subplot(2, 1, 1)
        plt.plot(equity_curve['date'], equity_curve['equity'], label='资金曲线', linewidth=2)
        plt.axhline(y=backtest_result['initial_capital'], color='r', linestyle='--', label='初始资金')
        plt.title(f"{backtest_result['symbol']} 资金曲线", fontsize=14, fontweight='bold')
        plt.xlabel('日期')
        plt.ylabel('资金 ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # 绘制回撤
        plt.subplot(2, 1, 2)
        equity_series = pd.Series(equity_curve['equity'].values)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100

        plt.fill_between(range(len(drawdown)), drawdown, 0, alpha=0.3, color='red')
        plt.plot(drawdown, color='red', linewidth=1)
        plt.title('回撤曲线', fontsize=14, fontweight='bold')
        plt.xlabel('交易日')
        plt.ylabel('回撤 (%)')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def plot_trade_analysis(self, backtest_result: Dict, filename: str = 'trade_analysis.png'):
        """
        绘制交易分析图

        Args:
            backtest_result: 回测结果
            filename: 输出文件名
        """
        trades = backtest_result['trades']

        # 计算每笔交易的收益
        trade_returns = []
        for i in range(0, len(trades) - 1, 2):
            if i + 1 < len(trades):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                return_pct = (sell_trade['price'] - buy_trade['price']) / buy_trade['price'] * 100
                trade_returns.append(return_pct)

        if not trade_returns:
            return None

        plt.figure(figsize=(14, 10))

        # 1. 交易收益分布
        plt.subplot(2, 2, 1)
        plt.bar(range(len(trade_returns)), trade_returns,
                color=['green' if r > 0 else 'red' for r in trade_returns])
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        plt.title('每笔交易收益', fontsize=12, fontweight='bold')
        plt.xlabel('交易序号')
        plt.ylabel('收益率 (%)')
        plt.grid(True, alpha=0.3)

        # 2. 收益分布直方图
        plt.subplot(2, 2, 2)
        plt.hist(trade_returns, bins=20, edgecolor='black', alpha=0.7)
        plt.axvline(x=0, color='red', linestyle='--', linewidth=2)
        plt.title('收益分布', fontsize=12, fontweight='bold')
        plt.xlabel('收益率 (%)')
        plt.ylabel('频数')
        plt.grid(True, alpha=0.3)

        # 3. 累计收益
        plt.subplot(2, 2, 3)
        cumulative_returns = np.cumsum(trade_returns)
        plt.plot(cumulative_returns, linewidth=2, color='blue')
        plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
        plt.title('累计收益', fontsize=12, fontweight='bold')
        plt.xlabel('交易序号')
        plt.ylabel('累计收益率 (%)')
        plt.grid(True, alpha=0.3)

        # 4. 盈亏比较
        plt.subplot(2, 2, 4)
        profits = [r for r in trade_returns if r > 0]
        losses = [abs(r) for r in trade_returns if r < 0]

        data = [len(profits), len(losses)]
        labels = [f'盈利 ({len(profits)})', f'亏损 ({len(losses)})']
        colors = ['green', 'red']

        plt.pie(data, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('盈亏比例', fontsize=12, fontweight='bold')

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def plot_strategy_comparison(self, comparison_df: pd.DataFrame, filename: str = 'strategy_comparison.png'):
        """
        绘制策略对比图

        Args:
            comparison_df: 策略对比 DataFrame
            filename: 输出文件名
        """
        plt.figure(figsize=(14, 10))

        # 1. 收益率对比
        plt.subplot(2, 2, 1)
        plt.bar(comparison_df['strategy'], comparison_df['total_return_pct'])
        plt.title('总收益率对比', fontsize=12, fontweight='bold')
        plt.xlabel('策略')
        plt.ylabel('收益率 (%)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        # 2. 胜率对比
        plt.subplot(2, 2, 2)
        plt.bar(comparison_df['strategy'], comparison_df['win_rate_pct'], color='green')
        plt.title('胜率对比', fontsize=12, fontweight='bold')
        plt.xlabel('策略')
        plt.ylabel('胜率 (%)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        # 3. 最大回撤对比
        plt.subplot(2, 2, 3)
        plt.bar(comparison_df['strategy'], comparison_df['max_drawdown_pct'], color='red')
        plt.title('最大回撤对比', fontsize=12, fontweight='bold')
        plt.xlabel('策略')
        plt.ylabel('最大回撤 (%)')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        # 4. 交易次数对比
        plt.subplot(2, 2, 4)
        plt.bar(comparison_df['strategy'], comparison_df['total_trades'], color='orange')
        plt.title('交易次数对比', fontsize=12, fontweight='bold')
        plt.xlabel('策略')
        plt.ylabel('交易次数')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def generate_report(self, backtest_result: Dict, metrics: Dict, filename: str = 'report.html'):
        """
        生成 HTML 报告

        Args:
            backtest_result: 回测结果
            metrics: 性能指标
            filename: 输出文件名
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>DY 策略回测报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .positive {{ color: green; font-weight: bold; }}
                .negative {{ color: red; font-weight: bold; }}
                .metric-box {{ display: inline-block; margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>DY 策略回测报告</h1>
            <p>股票代码: <strong>{backtest_result['symbol']}</strong></p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h2>核心指标</h2>
            <div>
                <div class="metric-box">
                    <h3>总收益率</h3>
                    <p class="{'positive' if metrics['total_return_pct'] > 0 else 'negative'}">
                        {metrics['total_return_pct']:.2f}%
                    </p>
                </div>
                <div class="metric-box">
                    <h3>年化收益率</h3>
                    <p class="{'positive' if metrics['annual_return_pct'] > 0 else 'negative'}">
                        {metrics['annual_return_pct']:.2f}%
                    </p>
                </div>
                <div class="metric-box">
                    <h3>最大回撤</h3>
                    <p class="negative">{metrics['max_drawdown_pct']:.2f}%</p>
                </div>
                <div class="metric-box">
                    <h3>胜率</h3>
                    <p>{metrics['win_rate_pct']:.2f}%</p>
                </div>
            </div>

            <h2>风险指标</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                </tr>
                <tr>
                    <td>夏普比率</td>
                    <td>{metrics['sharpe_ratio']:.2f}</td>
                </tr>
                <tr>
                    <td>索提诺比率</td>
                    <td>{metrics['sortino_ratio']:.2f}</td>
                </tr>
                <tr>
                    <td>卡玛比率</td>
                    <td>{metrics['calmar_ratio']:.2f}</td>
                </tr>
                <tr>
                    <td>盈亏比</td>
                    <td>{metrics['profit_factor']:.2f}</td>
                </tr>
            </table>

            <h2>交易统计</h2>
            <table>
                <tr>
                    <th>指标</th>
                    <th>数值</th>
                </tr>
                <tr>
                    <td>总交易次数</td>
                    <td>{metrics['total_trades']}</td>
                </tr>
                <tr>
                    <td>盈利次数</td>
                    <td class="positive">{metrics['winning_trades']}</td>
                </tr>
                <tr>
                    <td>亏损次数</td>
                    <td class="negative">{metrics['losing_trades']}</td>
                </tr>
                <tr>
                    <td>最大连续盈利</td>
                    <td>{metrics['max_consecutive_wins']}</td>
                </tr>
                <tr>
                    <td>最大连续亏损</td>
                    <td>{metrics['max_consecutive_losses']}</td>
                </tr>
                <tr>
                    <td>平均盈利</td>
                    <td class="positive">${metrics['avg_profit']:.2f}</td>
                </tr>
                <tr>
                    <td>平均亏损</td>
                    <td class="negative">${metrics['avg_loss']:.2f}</td>
                </tr>
            </table>
        </body>
        </html>
        """

        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return filepath


if __name__ == '__main__':
    # 示例：生成性能报告
    analyzer = PerformanceAnalyzer()

    # 模拟回测结果
    backtest_result = {
        'symbol': 'AAPL',
        'initial_capital': 100000,
        'final_capital': 115000,
        'total_return': 0.15,
        'total_return_pct': 15.0,
        'max_drawdown': -0.08,
        'max_drawdown_pct': -8.0,
        'total_trades': 10,
        'winning_trades': 7,
        'win_rate': 0.7,
        'win_rate_pct': 70.0,
        'trades': [],
        'equity_curve': []
    }

    metrics = analyzer.calculate_metrics(backtest_result)
    print("性能指标:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
