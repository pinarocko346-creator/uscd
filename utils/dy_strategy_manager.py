"""
DY 策略组合管理器
支持自定义策略组合和策略参数配置
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class StrategyManager:
    """策略组合管理器"""

    def __init__(self, config_dir: str = 'config/strategies'):
        """
        初始化策略管理器

        Args:
            config_dir: 策略配置文件目录
        """
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

        # 预定义策略
        self.predefined_strategies = {
            'aggressive': {
                'name': '激进策略',
                'description': '只要有买入信号就交易',
                'conditions': {
                    'buy': True
                },
                'risk_level': 'high',
                'expected_return': '5-15%',
                'holding_period': '1-5天'
            },
            'stable': {
                'name': '稳健策略',
                'description': '买入信号 + UP1（突破蓝带）',
                'conditions': {
                    'buy': True,
                    'up1': True
                },
                'risk_level': 'medium',
                'expected_return': '8-20%',
                'holding_period': '5-15天'
            },
            'strongest': {
                'name': '最强策略',
                'description': '买入信号 + UP3（蓝带突破黄带）',
                'conditions': {
                    'buy': True,
                    'up3': True
                },
                'risk_level': 'low',
                'expected_return': '15-40%',
                'holding_period': '15-30天'
            },
            'conservative': {
                'name': '保守策略',
                'description': '买入信号 + UP1 + UP2',
                'conditions': {
                    'buy': True,
                    'up1': True,
                    'up2': True
                },
                'risk_level': 'very_low',
                'expected_return': '10-25%',
                'holding_period': '10-20天'
            }
        }

    def create_custom_strategy(
        self,
        name: str,
        description: str,
        conditions: Dict,
        risk_level: str = 'medium',
        expected_return: str = '',
        holding_period: str = ''
    ) -> Dict:
        """
        创建自定义策略

        Args:
            name: 策略名称
            description: 策略描述
            conditions: 策略条件字典
            risk_level: 风险等级
            expected_return: 预期收益
            holding_period: 持仓周期

        Returns:
            策略配置字典
        """
        strategy = {
            'name': name,
            'description': description,
            'conditions': conditions,
            'risk_level': risk_level,
            'expected_return': expected_return,
            'holding_period': holding_period,
            'created_at': datetime.now().isoformat(),
            'custom': True
        }

        return strategy

    def save_strategy(self, strategy_id: str, strategy: Dict) -> bool:
        """
        保存策略到文件

        Args:
            strategy_id: 策略 ID
            strategy: 策略配置

        Returns:
            是否保存成功
        """
        try:
            filepath = os.path.join(self.config_dir, f'{strategy_id}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(strategy, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存策略失败: {e}")
            return False

    def load_strategy(self, strategy_id: str) -> Optional[Dict]:
        """
        加载策略

        Args:
            strategy_id: 策略 ID

        Returns:
            策略配置字典，如果不存在返回 None
        """
        # 先检查预定义策略
        if strategy_id in self.predefined_strategies:
            return self.predefined_strategies[strategy_id]

        # 再检查自定义策略
        try:
            filepath = os.path.join(self.config_dir, f'{strategy_id}.json')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载策略失败: {e}")

        return None

    def list_strategies(self) -> List[Dict]:
        """
        列出所有策略

        Returns:
            策略列表
        """
        strategies = []

        # 添加预定义策略
        for strategy_id, strategy in self.predefined_strategies.items():
            strategies.append({
                'id': strategy_id,
                'custom': False,
                **strategy
            })

        # 添加自定义策略
        try:
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    strategy_id = filename[:-5]
                    strategy = self.load_strategy(strategy_id)
                    if strategy:
                        strategies.append({
                            'id': strategy_id,
                            **strategy
                        })
        except Exception as e:
            print(f"列出策略失败: {e}")

        return strategies

    def delete_strategy(self, strategy_id: str) -> bool:
        """
        删除自定义策略

        Args:
            strategy_id: 策略 ID

        Returns:
            是否删除成功
        """
        # 不能删除预定义策略
        if strategy_id in self.predefined_strategies:
            print("不能删除预定义策略")
            return False

        try:
            filepath = os.path.join(self.config_dir, f'{strategy_id}.json')
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"删除策略失败: {e}")
            return False

    def filter_stocks_by_strategy(self, stocks: List[Dict], strategy_id: str) -> List[Dict]:
        """
        根据策略筛选股票

        Args:
            stocks: 股票列表
            strategy_id: 策略 ID

        Returns:
            符合策略的股票列表
        """
        strategy = self.load_strategy(strategy_id)
        if not strategy:
            return []

        conditions = strategy['conditions']
        filtered = []

        for stock in stocks:
            match = True
            for key, value in conditions.items():
                if stock.get(key) != value:
                    match = False
                    break
            if match:
                filtered.append(stock)

        return filtered

    def create_portfolio(
        self,
        name: str,
        strategies: List[Dict],
        allocation: Dict[str, float] = None
    ) -> Dict:
        """
        创建策略组合

        Args:
            name: 组合名称
            strategies: 策略列表 [{'id': 'aggressive', 'weight': 0.3}, ...]
            allocation: 资金分配比例

        Returns:
            组合配置
        """
        if allocation is None:
            # 平均分配
            weight = 1.0 / len(strategies)
            allocation = {s['id']: weight for s in strategies}

        portfolio = {
            'name': name,
            'strategies': strategies,
            'allocation': allocation,
            'created_at': datetime.now().isoformat()
        }

        return portfolio

    def save_portfolio(self, portfolio_id: str, portfolio: Dict) -> bool:
        """保存组合"""
        try:
            filepath = os.path.join(self.config_dir, f'portfolio_{portfolio_id}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(portfolio, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存组合失败: {e}")
            return False

    def load_portfolio(self, portfolio_id: str) -> Optional[Dict]:
        """加载组合"""
        try:
            filepath = os.path.join(self.config_dir, f'portfolio_{portfolio_id}.json')
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载组合失败: {e}")
        return None


if __name__ == '__main__':
    # 示例：创建和管理策略
    manager = StrategyManager()

    # 列出所有策略
    print("所有策略:")
    for strategy in manager.list_strategies():
        print(f"  - {strategy['id']}: {strategy['name']}")

    # 创建自定义策略
    custom_strategy = manager.create_custom_strategy(
        name='我的策略',
        description='买入 + UP1 + UP2',
        conditions={'buy': True, 'up1': True, 'up2': True},
        risk_level='low'
    )

    # 保存策略
    manager.save_strategy('my_strategy', custom_strategy)
    print("\n已创建自定义策略: my_strategy")

    # 创建组合
    portfolio = manager.create_portfolio(
        name='平衡组合',
        strategies=[
            {'id': 'aggressive', 'weight': 0.3},
            {'id': 'stable', 'weight': 0.5},
            {'id': 'strongest', 'weight': 0.2}
        ]
    )

    manager.save_portfolio('balanced', portfolio)
    print("已创建策略组合: balanced")
