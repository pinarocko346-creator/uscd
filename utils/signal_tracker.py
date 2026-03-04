"""
历史信号记录和追踪模块
记录每日筛选信号，追踪信号表现
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class SignalTracker:
    """信号追踪器"""

    def __init__(self, db_path: str = 'signal_history.db'):
        """
        初始化信号追踪器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.conn = None
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(str(self.db_path))
        cursor = self.conn.cursor()

        # 创建信号记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                buy INTEGER NOT NULL,
                sell INTEGER NOT NULL,
                up1 INTEGER NOT NULL,
                up2 INTEGER NOT NULL,
                up3 INTEGER NOT NULL,
                down1 INTEGER NOT NULL,
                down2 INTEGER NOT NULL,
                down3 INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, symbol)
            )
        ''')

        # 创建信号追踪表（记录信号后的表现）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER NOT NULL,
                days_after INTEGER NOT NULL,
                price REAL NOT NULL,
                return_pct REAL NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals(id),
                UNIQUE(signal_id, days_after)
            )
        ''')

        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_buy ON signals(buy)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_sell ON signals(sell)')

        self.conn.commit()

    def save_signals(self, date: str, results: List[Dict]):
        """
        保存信号记录

        Args:
            date: 日期 'YYYY-MM-DD'
            results: 筛选结果列表
        """
        cursor = self.conn.cursor()

        for result in results:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO signals
                    (date, symbol, price, buy, sell, up1, up2, up3, down1, down2, down3)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    date,
                    result['symbol'],
                    result['price'],
                    1 if result['buy'] else 0,
                    1 if result['sell'] else 0,
                    1 if result['up1'] else 0,
                    1 if result['up2'] else 0,
                    1 if result['up3'] else 0,
                    1 if result['down1'] else 0,
                    1 if result['down2'] else 0,
                    1 if result['down3'] else 0
                ))
            except Exception as e:
                print(f"保存信号失败 {result['symbol']}: {e}")

        self.conn.commit()

    def update_performance(self, signal_id: int, days_after: int, current_price: float, entry_price: float):
        """
        更新信号表现

        Args:
            signal_id: 信号ID
            days_after: 信号后第几天
            current_price: 当前价格
            entry_price: 入场价格
        """
        return_pct = (current_price - entry_price) / entry_price * 100

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO signal_performance
            (signal_id, days_after, price, return_pct)
            VALUES (?, ?, ?, ?)
        ''', (signal_id, days_after, current_price, return_pct))

        self.conn.commit()

    def get_signals(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        symbol: Optional[str] = None,
        buy: Optional[bool] = None,
        sell: Optional[bool] = None
    ) -> pd.DataFrame:
        """
        查询信号记录

        Args:
            start_date: 开始日期
            end_date: 结束日期
            symbol: 股票代码
            buy: 是否有买入信号
            sell: 是否有卖出信号

        Returns:
            信号记录 DataFrame
        """
        query = 'SELECT * FROM signals WHERE 1=1'
        params = []

        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)

        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)

        if symbol:
            query += ' AND symbol = ?'
            params.append(symbol)

        if buy is not None:
            query += ' AND buy = ?'
            params.append(1 if buy else 0)

        if sell is not None:
            query += ' AND sell = ?'
            params.append(1 if sell else 0)

        query += ' ORDER BY date DESC, symbol'

        return pd.read_sql_query(query, self.conn, params=params)

    def get_signal_performance(self, signal_id: int) -> pd.DataFrame:
        """
        获取信号表现

        Args:
            signal_id: 信号ID

        Returns:
            表现记录 DataFrame
        """
        query = '''
            SELECT * FROM signal_performance
            WHERE signal_id = ?
            ORDER BY days_after
        '''
        return pd.read_sql_query(query, self.conn, params=(signal_id,))

    def analyze_strategy_performance(
        self,
        strategy: str,
        days: int = 5,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        分析策略表现

        Args:
            strategy: 策略类型 ('aggressive', 'stable', 'strongest')
            days: 持有天数
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            策略表现统计
        """
        # 根据策略类型构建查询条件
        if strategy == 'aggressive':
            condition = 'buy = 1'
        elif strategy == 'stable':
            condition = 'buy = 1 AND up1 = 1'
        elif strategy == 'strongest':
            condition = 'buy = 1 AND up3 = 1'
        else:
            condition = '1=1'

        query = f'''
            SELECT
                s.id,
                s.date,
                s.symbol,
                s.price as entry_price,
                sp.price as exit_price,
                sp.return_pct
            FROM signals s
            JOIN signal_performance sp ON s.id = sp.signal_id
            WHERE {condition}
            AND sp.days_after = ?
        '''

        params = [days]

        if start_date:
            query += ' AND s.date >= ?'
            params.append(start_date)

        if end_date:
            query += ' AND s.date <= ?'
            params.append(end_date)

        df = pd.read_sql_query(query, self.conn, params=params)

        if df.empty:
            return {
                'strategy': strategy,
                'total_signals': 0,
                'avg_return': 0,
                'win_rate': 0,
                'max_return': 0,
                'min_return': 0
            }

        return {
            'strategy': strategy,
            'total_signals': len(df),
            'avg_return': df['return_pct'].mean(),
            'win_rate': (df['return_pct'] > 0).sum() / len(df) * 100,
            'max_return': df['return_pct'].max(),
            'min_return': df['return_pct'].min(),
            'median_return': df['return_pct'].median(),
            'std_return': df['return_pct'].std()
        }

    def get_top_performers(
        self,
        days: int = 5,
        limit: int = 10,
        strategy: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取表现最好的信号

        Args:
            days: 持有天数
            limit: 返回数量
            strategy: 策略类型

        Returns:
            表现最好的信号 DataFrame
        """
        condition = '1=1'
        if strategy == 'aggressive':
            condition = 's.buy = 1'
        elif strategy == 'stable':
            condition = 's.buy = 1 AND s.up1 = 1'
        elif strategy == 'strongest':
            condition = 's.buy = 1 AND s.up3 = 1'

        query = f'''
            SELECT
                s.date,
                s.symbol,
                s.price as entry_price,
                sp.price as exit_price,
                sp.return_pct
            FROM signals s
            JOIN signal_performance sp ON s.id = sp.signal_id
            WHERE {condition}
            AND sp.days_after = ?
            ORDER BY sp.return_pct DESC
            LIMIT ?
        '''

        return pd.read_sql_query(query, self.conn, params=(days, limit))

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    # 示例：使用信号追踪器
    tracker = SignalTracker()

    # 保存今天的信号
    today = datetime.now().strftime('%Y-%m-%d')
    test_signals = [
        {
            'symbol': 'AAPL',
            'price': 175.23,
            'buy': True,
            'sell': False,
            'up1': True,
            'up2': True,
            'up3': False,
            'down1': False,
            'down2': False,
            'down3': False
        },
        {
            'symbol': 'MSFT',
            'price': 420.15,
            'buy': True,
            'sell': False,
            'up1': True,
            'up2': False,
            'up3': False,
            'down1': False,
            'down2': False,
            'down3': False
        }
    ]

    tracker.save_signals(today, test_signals)
    print(f"已保存 {len(test_signals)} 条信号记录")

    # 查询买入信号
    buy_signals = tracker.get_signals(buy=True)
    print(f"\n买入信号数量: {len(buy_signals)}")

    # 分析策略表现
    performance = tracker.analyze_strategy_performance('stable', days=5)
    print(f"\n稳健策略表现:")
    print(f"  总信号数: {performance['total_signals']}")
    print(f"  平均收益: {performance['avg_return']:.2f}%")
    print(f"  胜率: {performance['win_rate']:.2f}%")

    tracker.close()
