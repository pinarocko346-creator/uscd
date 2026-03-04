"""
DY 策略对比分析工具
支持多策略对比和综合评估
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from .dy_backtest import BacktestEngine
from .dy_performance import PerformanceAnalyzer
import os


class StrategyComparator:
    """策略对比分析器"""

    def __init__(self, initial_capital: float = 100000):
        """
        初始化对比分析器

        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.backtest_engine = BacktestEngine(initial_capital=initial_capital)
        self.performance_analyzer = PerformanceAnalyzer()

    def compare_strategies_single_stock(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        strategies: List[str] = None
    ) -> pd.DataFrame:
        """
        对比单个股票的多个策略

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            strategies: 策略列表

        Returns:
            对比结果 DataFrame
        """
        if strategies is None:
            strategies = ['buy_signal', 'stable', 'strongest']

        results = []

        for strategy in strategies:
            print(f"回测策略: {strategy}")
            backtest_result = self.backtest_engine.backtest_single_stock(
                symbol, start_date, end_date, strategy
            )

            if backtest_result:
                metrics = self.performance_analyzer.calculate_metrics(backtest_result)

                results.append({
                    'strategy': strategy,
                    'symbol': symbol,
                    'total_return_pct': metrics['total_return_pct'],
                    'annual_return_pct': metrics['annual_return_pct'],
                    'max_drawdown_pct': metrics['max_drawdown_pct'],
                    'sharpe_ratio': metrics['sharpe_ratio'],
                    'sortino_ratio': metrics['sortino_ratio'],
                    'win_rate_pct': metrics['win_rate_pct'],
                    'total_trades': metrics['total_trades'],
                    'profit_factor': metrics['profit_factor']
                })

        return pd.DataFrame(results)

    def compare_strategies_portfolio(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategies: List[str] = None
    ) -> pd.DataFrame:
        """
        对比投资组合的多个策略

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            strategies: 策略列表

        Returns:
            对比结果 DataFrame
        """
        if strategies is None:
            strategies = ['buy_signal', 'stable', 'strongest']

        results = []

        for strategy in strategies:
            print(f"\n回测策略: {strategy}")
            portfolio_result = self.backtest_engine.backtest_portfolio(
                symbols, start_date, end_date, strategy
            )

            if portfolio_result:
                results.append({
                    'strategy': strategy,
                    'num_stocks': portfolio_result['num_stocks'],
                    'avg_total_return_pct': portfolio_result['avg_total_return_pct'],
                    'avg_win_rate_pct': portfolio_result['avg_win_rate_pct'],
                    'avg_max_drawdown_pct': portfolio_result['avg_max_drawdown_pct']
                })

        return pd.DataFrame(results)

    def rank_strategies(self, comparison_df: pd.DataFrame, weights: Dict[str, float] = None) -> pd.DataFrame:
        """
        对策略进行综合排名

        Args:
            comparison_df: 对比结果 DataFrame
            weights: 指标权重字典

        Returns:
            排名结果 DataFrame
        """
        if weights is None:
            weights = {
                'total_return_pct': 0.3,
                'sharpe_ratio': 0.25,
                'win_rate_pct': 0.2,
                'max_drawdown_pct': 0.15,  # 负向指标
                'profit_factor': 0.1
            }

        df = comparison_df.copy()

        # 标准化各指标（0-1 范围）
        for col in weights.keys():
            if col in df.columns:
                if col == 'max_drawdown_pct':
                    # 回撤是负向指标，取绝对值后反向标准化
                    df[f'{col}_norm'] = 1 - (abs(df[col]) - abs(df[col]).min()) / (abs(df[col]).max() - abs(df[col]).min() + 1e-10)
                else:
                    # 正向指标
                    df[f'{col}_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min() + 1e-10)

        # 计算综合得分
        df['score'] = 0
        for col, weight in weights.items():
            if f'{col}_norm' in df.columns:
                df['score'] += df[f'{col}_norm'] * weight

        # 排名
        df['rank'] = df['score'].rank(ascending=False)
        df = df.sort_values('rank')

        return df

    def generate_comparison_report(
        self,
        comparison_df: pd.DataFrame,
        output_file: str = 'strategy_comparison_report.html'
    ) -> str:
        """
        生成策略对比报告

        Args:
            comparison_df: 对比结果 DataFrame
            output_file: 输出文件名

        Returns:
            报告文件路径
        """
        # 生成对比图表
        chart_path = self.performance_analyzer.plot_strategy_comparison(comparison_df)

        # 生成 HTML 报告
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>DY 策略对比报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                h2 {{ color: #666; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .best {{ background-color: #d4edda; font-weight: bold; }}
                .worst {{ background-color: #f8d7da; }}
                img {{ max-width: 100%; height: auto; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>DY 策略对比报告</h1>

            <h2>策略对比表</h2>
            <table>
                <tr>
                    <th>策略</th>
                    <th>总收益率 (%)</th>
                    <th>年化收益率 (%)</th>
                    <th>最大回撤 (%)</th>
                    <th>夏普比率</th>
                    <th>胜率 (%)</th>
                    <th>交易次数</th>
                    <th>盈亏比</th>
                </tr>
        """

        # 找出最佳和最差值
        best_return = comparison_df['total_return_pct'].max()
        best_sharpe = comparison_df['sharpe_ratio'].max() if 'sharpe_ratio' in comparison_df.columns else 0
        best_win_rate = comparison_df['win_rate_pct'].max()
        worst_drawdown = comparison_df['max_drawdown_pct'].min()

        for _, row in comparison_df.iterrows():
            html += "<tr>"
            html += f"<td><strong>{row['strategy']}</strong></td>"

            # 总收益率
            css_class = 'best' if row['total_return_pct'] == best_return else ''
            html += f"<td class='{css_class}'>{row['total_return_pct']:.2f}</td>"

            # 年化收益率
            if 'annual_return_pct' in row:
                html += f"<td>{row['annual_return_pct']:.2f}</td>"
            else:
                html += "<td>-</td>"

            # 最大回撤
            css_class = 'best' if row['max_drawdown_pct'] == worst_drawdown else ''
            html += f"<td class='{css_class}'>{row['max_drawdown_pct']:.2f}</td>"

            # 夏普比率
            if 'sharpe_ratio' in row:
                css_class = 'best' if row['sharpe_ratio'] == best_sharpe else ''
                html += f"<td class='{css_class}'>{row['sharpe_ratio']:.2f}</td>"
            else:
                html += "<td>-</td>"

            # 胜率
            css_class = 'best' if row['win_rate_pct'] == best_win_rate else ''
            html += f"<td class='{css_class}'>{row['win_rate_pct']:.2f}</td>"

            # 交易次数
            html += f"<td>{row['total_trades']}</td>"

            # 盈亏比
            if 'profit_factor' in row:
                html += f"<td>{row['profit_factor']:.2f}</td>"
            else:
                html += "<td>-</td>"

            html += "</tr>"

        html += """
            </table>

            <h2>策略对比图表</h2>
            <img src="strategy_comparison.png" alt="策略对比图表">

            <h2>策略建议</h2>
            <ul>
        """

        # 生成建议
        best_strategy = comparison_df.loc[comparison_df['total_return_pct'].idxmax(), 'strategy']
        safest_strategy = comparison_df.loc[comparison_df['max_drawdown_pct'].idxmax(), 'strategy']
        most_consistent = comparison_df.loc[comparison_df['win_rate_pct'].idxmax(), 'strategy']

        html += f"<li><strong>最高收益策略</strong>: {best_strategy} (收益率: {comparison_df['total_return_pct'].max():.2f}%)</li>"
        html += f"<li><strong>最安全策略</strong>: {safest_strategy} (最大回撤: {comparison_df['max_drawdown_pct'].max():.2f}%)</li>"
        html += f"<li><strong>最稳定策略</strong>: {most_consistent} (胜率: {comparison_df['win_rate_pct'].max():.2f}%)</li>"

        html += """
            </ul>
        </body>
        </html>
        """

        filepath = os.path.join(self.performance_analyzer.output_dir, output_file)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return filepath

    def find_best_strategy(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        strategies: List[str] = None,
        criterion: str = 'total_return'
    ) -> Dict:
        """
        找出最佳策略

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            strategies: 策略列表
            criterion: 评判标准 ('total_return', 'sharpe_ratio', 'win_rate')

        Returns:
            最佳策略信息
        """
        comparison_df = self.compare_strategies_portfolio(
            symbols, start_date, end_date, strategies
        )

        if comparison_df.empty:
            return None

        criterion_map = {
            'total_return': 'avg_total_return_pct',
            'sharpe_ratio': 'sharpe_ratio',
            'win_rate': 'avg_win_rate_pct'
        }

        col = criterion_map.get(criterion, 'avg_total_return_pct')

        if col in comparison_df.columns:
            best_idx = comparison_df[col].idxmax()
            best_strategy = comparison_df.loc[best_idx]

            return {
                'strategy': best_strategy['strategy'],
                'criterion': criterion,
                'value': best_strategy[col],
                'details': best_strategy.to_dict()
            }

        return None


if __name__ == '__main__':
    # 示例：对比策略
    comparator = StrategyComparator(initial_capital=100000)

    # 对比单个股票的策略
    comparison = comparator.compare_strategies_single_stock(
        symbol='AAPL',
        start_date='2023-01-01',
        end_date='2024-01-01'
    )

    print("策略对比结果:")
    print(comparison)

    # 生成对比报告
    if not comparison.empty:
        report_path = comparator.generate_comparison_report(comparison)
        print(f"\n对比报告已生成: {report_path}")
