"""
自定义策略组合模块
允许用户创建和管理自定义的筛选策略
"""

import json
from typing import Dict, List, Any
from pathlib import Path


class CustomStrategy:
    """自定义策略类"""

    def __init__(self, name: str, description: str, conditions: Dict[str, Any]):
        """
        初始化自定义策略

        Args:
            name: 策略名称
            description: 策略描述
            conditions: 筛选条件字典
        """
        self.name = name
        self.description = description
        self.conditions = conditions

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'name': self.name,
            'description': self.description,
            'conditions': self.conditions
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CustomStrategy':
        """从字典创建"""
        return cls(
            name=data['name'],
            description=data['description'],
            conditions=data['conditions']
        )

    def apply(self, results: List[Dict]) -> List[Dict]:
        """
        应用策略筛选

        Args:
            results: 股票结果列表

        Returns:
            筛选后的结果
        """
        filtered = []

        for result in results:
            if self._match_conditions(result):
                filtered.append(result)

        return filtered

    def _match_conditions(self, result: Dict) -> bool:
        """检查是否匹配条件"""
        conditions = self.conditions

        # 买卖信号条件
        if 'buy' in conditions and result['buy'] != conditions['buy']:
            return False
        if 'sell' in conditions and result['sell'] != conditions['sell']:
            return False

        # 趋势信号条件（AND 逻辑）
        if 'up1' in conditions and result['up1'] != conditions['up1']:
            return False
        if 'up2' in conditions and result['up2'] != conditions['up2']:
            return False
        if 'up3' in conditions and result['up3'] != conditions['up3']:
            return False
        if 'down1' in conditions and result['down1'] != conditions['down1']:
            return False
        if 'down2' in conditions and result['down2'] != conditions['down2']:
            return False
        if 'down3' in conditions and result['down3'] != conditions['down3']:
            return False

        # 价格范围条件
        if 'min_price' in conditions and result['price'] < conditions['min_price']:
            return False
        if 'max_price' in conditions and result['price'] > conditions['max_price']:
            return False

        # 组合条件（OR 逻辑）
        if 'any_up' in conditions and conditions['any_up']:
            if not (result['up1'] or result['up2'] or result['up3']):
                return False

        if 'any_down' in conditions and conditions['any_down']:
            if not (result['down1'] or result['down2'] or result['down3']):
                return False

        return True


class StrategyManager:
    """策略管理器"""

    def __init__(self, storage_path: str = 'custom_strategies.json'):
        """
        初始化策略管理器

        Args:
            storage_path: 策略存储文件路径
        """
        self.storage_path = Path(storage_path)
        self.strategies: Dict[str, CustomStrategy] = {}
        self._load_strategies()

    def _load_strategies(self):
        """从文件加载策略"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for strategy_data in data:
                        strategy = CustomStrategy.from_dict(strategy_data)
                        self.strategies[strategy.name] = strategy
            except Exception as e:
                print(f"加载策略失败: {e}")

    def _save_strategies(self):
        """保存策略到文件"""
        try:
            data = [strategy.to_dict() for strategy in self.strategies.values()]
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存策略失败: {e}")

    def add_strategy(self, strategy: CustomStrategy) -> bool:
        """
        添加策略

        Args:
            strategy: 自定义策略

        Returns:
            是否成功
        """
        if strategy.name in self.strategies:
            return False

        self.strategies[strategy.name] = strategy
        self._save_strategies()
        return True

    def update_strategy(self, name: str, strategy: CustomStrategy) -> bool:
        """
        更新策略

        Args:
            name: 原策略名称
            strategy: 新策略

        Returns:
            是否成功
        """
        if name not in self.strategies:
            return False

        # 如果改名了，删除旧的
        if name != strategy.name:
            del self.strategies[name]

        self.strategies[strategy.name] = strategy
        self._save_strategies()
        return True

    def delete_strategy(self, name: str) -> bool:
        """
        删除策略

        Args:
            name: 策略名称

        Returns:
            是否成功
        """
        if name not in self.strategies:
            return False

        del self.strategies[name]
        self._save_strategies()
        return True

    def get_strategy(self, name: str) -> CustomStrategy:
        """获取策略"""
        return self.strategies.get(name)

    def list_strategies(self) -> List[Dict]:
        """列出所有策略"""
        return [
            {
                'name': strategy.name,
                'description': strategy.description
            }
            for strategy in self.strategies.values()
        ]

    def apply_strategy(self, name: str, results: List[Dict]) -> List[Dict]:
        """
        应用策略

        Args:
            name: 策略名称
            results: 股票结果列表

        Returns:
            筛选后的结果
        """
        strategy = self.get_strategy(name)
        if not strategy:
            return results

        return strategy.apply(results)


# 预定义一些常用策略模板
STRATEGY_TEMPLATES = {
    'conservative': CustomStrategy(
        name='保守型',
        description='买入信号 + UP3，追求确定性',
        conditions={'buy': True, 'up3': True}
    ),
    'balanced': CustomStrategy(
        name='平衡型',
        description='买入信号 + UP1，平衡收益风险',
        conditions={'buy': True, 'up1': True}
    ),
    'aggressive': CustomStrategy(
        name='激进型',
        description='只看买入信号，追求高收益',
        conditions={'buy': True}
    ),
    'strong_momentum': CustomStrategy(
        name='强势动量',
        description='买入 + UP2 + UP3，双重确认',
        conditions={'buy': True, 'up2': True, 'up3': True}
    ),
    'breakout': CustomStrategy(
        name='突破策略',
        description='买入 + 任意上涨趋势',
        conditions={'buy': True, 'any_up': True}
    ),
    'risk_control': CustomStrategy(
        name='风险控制',
        description='卖出信号 + 下跌趋势',
        conditions={'sell': True, 'any_down': True}
    ),
    'high_price': CustomStrategy(
        name='高价股',
        description='买入信号 + 价格 > $100',
        conditions={'buy': True, 'min_price': 100}
    ),
    'low_price': CustomStrategy(
        name='低价股',
        description='买入信号 + 价格 < $10',
        conditions={'buy': True, 'max_price': 10}
    ),
}


if __name__ == '__main__':
    # 示例：创建和使用自定义策略
    manager = StrategyManager()

    # 添加预定义策略
    for template in STRATEGY_TEMPLATES.values():
        manager.add_strategy(template)

    # 创建自定义策略
    my_strategy = CustomStrategy(
        name='我的策略',
        description='买入 + UP1 + UP2，价格在 $50-$200',
        conditions={
            'buy': True,
            'up1': True,
            'up2': True,
            'min_price': 50,
            'max_price': 200
        }
    )
    manager.add_strategy(my_strategy)

    # 列出所有策略
    print("已保存的策略:")
    for strategy in manager.list_strategies():
        print(f"  - {strategy['name']}: {strategy['description']}")

    # 测试应用策略
    test_results = [
        {'symbol': 'AAPL', 'price': 175, 'buy': True, 'sell': False,
         'up1': True, 'up2': True, 'up3': False,
         'down1': False, 'down2': False, 'down3': False},
        {'symbol': 'MSFT', 'price': 420, 'buy': True, 'sell': False,
         'up1': True, 'up2': False, 'up3': False,
         'down1': False, 'down2': False, 'down3': False},
        {'symbol': 'GOOGL', 'price': 140, 'buy': True, 'sell': False,
         'up1': False, 'up2': False, 'up3': True,
         'down1': False, 'down2': False, 'down3': False},
    ]

    print("\n应用'我的策略':")
    filtered = manager.apply_strategy('我的策略', test_results)
    for result in filtered:
        print(f"  {result['symbol']}: ${result['price']}")
