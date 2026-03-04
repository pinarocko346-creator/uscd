"""
DY 历史信号记录和追踪
记录每日信号并支持历史查询和分析
"""

import sqlite3
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os


class SignalTracker:
    """信号追踪器"""

    def __init__(self, db_path: str = 'data/dy_signals.db'):
        """
        初始化信号追踪器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()

    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建信号记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                buy INTEGER DEFAULT 0,
                sell INTEGER DEFAULT 0,
                up1 INTEGER DEFAULT 0,
                up2 INTEGER DEFAULT 0,
                up3 INTEGER DEFAULT 0,
                down1 INTEGER DEFAULT 0,
                down2 INTEGER DEFAULT 0,
                down3 INTEGER DEFAULT 0,
                blue_top REAL,
                blue_bottom REAL,
                yellow_top REAL,
                yellow_bottom REAL,
                diff REAL,
                dea REAL,
                macd REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, symbol)
            )
        ''')

        # 创建信号追踪表（记录信号后的表现）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                signal_date TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                exit_date TEXT,
                return_pct REAL,
                holding_days INTEGER,
                status TEXT DEFAULT 'open',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (signal_id) REFERENCES signals(id)
            )
        ''')

        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_symbol ON signal_performance(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_performance_status ON signal_performance(status)')

        conn.commit()
        conn.close()

    def save_signal(self, signal: Dict) -> bool:
        """
        保存信号

        Args:
            signal: 信号字典

        Returns:
            是否保存成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO signals
                (date, symbol, price, buy, sell, up1, up2, up3, down1, down2, down3,
                 blue_top, blue_bottom, yellow_top, yellow_bottom, diff, dea, macd)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal['date'],
                signal['symbol'],
                signal['price'],
                int(signal.get('buy', False)),
                int(signal.get('sell', False)),
                int(signal.get('up1', False)),
                int(signal.get('up2', False)),
                int(signal.get('up3', False)),
                int(signal.get('down1', False)),
                int(signal.get('down2', False)),
                int(signal.get('down3', False)),
                signal.get('blue_top'),
                signal.get('blue_bottom'),
                signal.get('yellow_top'),
                signal.get('yellow_bottom'),
                signal.get('diff'),
                signal.get('dea'),
                signal.get('macd')
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"保存信号失败: {e}")
            return False

    def save_signals_batch(self, signals: List[Dict]) -> int:
        """
        批量保存信号

        Args:
            signals: 信号列表

        Returns:
            成功保存的数量
        """
        count = 0
        for signal in signals:
            if self.save_signal(signal):
                count += 1
        return count

    def get_signals(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        signal_type: Optional[str] = None
    ) -> pd.DataFrame:
        """
        查询信号

        Args:
            symbol: 股票代码（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            signal_type: 信号类型 ('buy', 'sell', 'up1', etc.)

        Returns:
            信号 DataFrame
        """
        conn = sqlite3.connect(self.db_path)

        query = "SELECT * FROM signals WHERE 1=1"
        params = []

        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        if signal_type:
            query += f" AND {signal_type} = 1"

        query += " ORDER BY date DESC, symbol"

        df = pd.read_sql_query(query, conn, params=params)
        conn.close()

        return df

    def track_signal_performance(
        self,
        signal_id: int,
        symbol: str,
        signal_date: str,
        signal_type: str,
        entry_price: float
    ) -> bool:
        """
        开始追踪信号表现

        Args:
            signal_id: 信号 ID
            symbol: 股票代码
            signal_date: 信号日期
            signal_type: 信号类型
            entry_price: 入场价格

        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO signal_performance
                (signal_id, symbol, signal_date, signal_type, entry_price, status)
                VALUES (?, ?, ?, ?, ?, 'open')
            ''', (signal_id, symbol, signal_date, signal_type, entry_price))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"追踪信号失败: {e}")
            return False

    def close_signal_performance(
        self,
        performance_id: int,
        exit_price: float,
        exit_date: str
    ) -> bool:
        """
        关闭信号追踪

        Args:
            performance_id: 追踪记录 ID
            exit_price: 出场价格
            exit_date: 出场日期

        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 获取入场信息
            cursor.execute('''
                SELECT entry_price, signal_date
                FROM signal_performance
                WHERE id = ?
            ''', (performance_id,))

            row = cursor.fetchone()
            if not row:
                return False

            entry_price, signal_date = row

            # 计算收益和持仓天数
            return_pct = (exit_price - entry_price) / entry_price * 100
            holding_days = (datetime.strptime(exit_date, '%Y-%m-%d') -
                          datetime.strptime(signal_date, '%Y-%m-%d')).days

            # 更新记录
            cursor.execute('''
                UPDATE signal_performance
                SET exit_price = ?,
                    exit_date = ?,
                    return_pct = ?,
                    holding_days = ?,
                    status = 'closed'
                WHERE id = ?
            ''', (exit_price, exit_date, return_pct, holding_days, performance_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"关闭信号追踪失败: {e}")
            return False

    def get_signal_statistics(
        self,
        symbol: Optional[str] = None,
        signal_type: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        获取信号统计

        Args:
            symbol: 股票代码（可选）
            signal_type: 信号类型（可选）
            days: 统计天数

        Returns:
            统计结果字典
        """
        conn = sqlite3.connect(self.db_path)

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = '''
            SELECT
                COUNT(*) as total_signals,
                SUM(buy) as buy_signals,
                SUM(sell) as sell_signals,
                SUM(up1) as up1_signals,
                SUM(up2) as up2_signals,
                SUM(up3) as up3_signals,
                SUM(down1) as down1_signals,
                SUM(down2) as down2_signals,
                SUM(down3) as down3_signals
            FROM signals
            WHERE date >= ?
        '''

        params = [start_date]

        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)

        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()

        stats = {
            'total_signals': row[0],
            'buy_signals': row[1],
            'sell_signals': row[2],
            'up1_signals': row[3],
            'up2_signals': row[4],
            'up3_signals': row[5],
            'down1_signals': row[6],
            'down2_signals': row[7],
            'down3_signals': row[8]
        }

        # 获取表现统计
        perf_query = '''
            SELECT
                COUNT(*) as total_trades,
                AVG(return_pct) as avg_return,
                AVG(holding_days) as avg_holding_days,
                SUM(CASE WHEN return_pct > 0 THEN 1 ELSE 0 END) as winning_trades
            FROM signal_performance
            WHERE signal_date >= ? AND status = 'closed'
        '''

        perf_params = [start_date]

        if symbol:
            perf_query += " AND symbol = ?"
            perf_params.append(symbol)

        if signal_type:
            perf_query += " AND signal_type = ?"
            perf_params.append(signal_type)

        cursor.execute(perf_query, perf_params)
        perf_row = cursor.fetchone()

        if perf_row[0]:
            stats['performance'] = {
                'total_trades': perf_row[0],
                'avg_return_pct': perf_row[1],
                'avg_holding_days': perf_row[2],
                'winning_trades': perf_row[3],
                'win_rate_pct': (perf_row[3] / perf_row[0] * 100) if perf_row[0] > 0 else 0
            }

        conn.close()
        return stats

    def get_top_performers(self, limit: int = 10, days: int = 30) -> pd.DataFrame:
        """
        获取表现最好的股票

        Args:
            limit: 返回数量
            days: 统计天数

        Returns:
            表现最好的股票 DataFrame
        """
        conn = sqlite3.connect(self.db_path)

        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = '''
            SELECT
                symbol,
                COUNT(*) as total_trades,
                AVG(return_pct) as avg_return,
                SUM(CASE WHEN return_pct > 0 THEN 1 ELSE 0 END) as winning_trades
            FROM signal_performance
            WHERE signal_date >= ? AND status = 'closed'
            GROUP BY symbol
            HAVING total_trades >= 3
            ORDER BY avg_return DESC
            LIMIT ?
        '''

        df = pd.read_sql_query(query, conn, params=[start_date, limit])
        conn.close()

        if not df.empty:
            df['win_rate_pct'] = (df['winning_trades'] / df['total_trades'] * 100)

        return df


if __name__ == '__main__':
    # 示例：使用信号追踪器
    tracker = SignalTracker()

    # 保存信号
    signal = {
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
    }

    tracker.save_signal(signal)
    print("已保存信号")

    # 查询信号
    signals = tracker.get_signals(symbol='AAPL', signal_type='buy')
    print(f"\nAAPL 买入信号: {len(signals)} 条")

    # 获取统计
    stats = tracker.get_signal_statistics(days=30)
    print(f"\n最近 30 天统计:")
    print(f"  总信号数: {stats['total_signals']}")
    print(f"  买入信号: {stats['buy_signals']}")
    print(f"  卖出信号: {stats['sell_signals']}")
