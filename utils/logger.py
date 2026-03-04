"""
日志系统模块
记录调仓、风险预警、性能统计等信息
"""
import logging
import os
from datetime import datetime
from typing import Dict, Any
import sys

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import LOG_DIR, LOG_LEVEL, LOG_TO_FILE


class Logger:
    """日志记录器"""

    def __init__(self, name: str = 'quant_system', log_dir: str = None):
        """
        初始化日志记录器

        Args:
            name: 日志名称
            log_dir: 日志目录
        """
        self.name = name
        self.log_dir = log_dir or LOG_DIR

        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # 创建logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))

        # 清除已有的handlers
        self.logger.handlers = []

        # 创建formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # 文件handler
        if LOG_TO_FILE:
            log_file = os.path.join(
                self.log_dir,
                f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, LOG_LEVEL))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def info(self, message: str):
        """记录信息"""
        self.logger.info(message)

    def warning(self, message: str):
        """记录警告"""
        self.logger.warning(message)

    def error(self, message: str):
        """记录错误"""
        self.logger.error(message)

    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)

    def log_rebalance(self, layer: str, date: str, holdings: Dict[str, float],
                      trades: Dict[str, Any]):
        """
        记录调仓信息

        Args:
            layer: 层级名称
            date: 日期
            holdings: 持仓字典 {股票代码: 仓位}
            trades: 交易信息 {'buy': [...], 'sell': [...]}
        """
        self.info(f"\n{'='*60}")
        self.info(f"{layer} - 调仓记录 - {date}")
        self.info(f"{'='*60}")

        if trades.get('sell'):
            self.info(f"卖出 ({len(trades['sell'])}只):")
            for stock in trades['sell']:
                self.info(f"  - {stock}")

        if trades.get('buy'):
            self.info(f"买入 ({len(trades['buy'])}只):")
            for stock in trades['buy']:
                self.info(f"  - {stock}")

        self.info(f"当前持仓 ({len(holdings)}只):")
        for stock, weight in holdings.items():
            self.info(f"  - {stock}: {weight*100:.2f}%")

        self.info(f"{'='*60}\n")

    def log_risk_alert(self, alert_type: str, level: str, message: str, data: Dict = None):
        """
        记录风险预警

        Args:
            alert_type: 预警类型
            level: 预警级别 ('INFO', 'WARNING', 'ERROR', 'CRITICAL')
            message: 预警信息
            data: 相关数据
        """
        log_message = f"[风险预警] {alert_type} - {message}"

        if data:
            log_message += f"\n  数据: {data}"

        if level == 'INFO':
            self.info(log_message)
        elif level == 'WARNING':
            self.warning(log_message)
        elif level == 'ERROR':
            self.error(log_message)
        elif level == 'CRITICAL':
            self.logger.critical(log_message)

    def log_performance(self, date: str, metrics: Dict[str, float]):
        """
        记录性能统计

        Args:
            date: 日期
            metrics: 性能指标字典
        """
        self.info(f"\n{'='*60}")
        self.info(f"性能统计 - {date}")
        self.info(f"{'='*60}")

        for key, value in metrics.items():
            if isinstance(value, float):
                self.info(f"{key:20s}: {value:10.4f}")
            else:
                self.info(f"{key:20s}: {value}")

        self.info(f"{'='*60}\n")

    def log_model_info(self, layer: str, model_type: str, info: Dict):
        """
        记录模型信息

        Args:
            layer: 层级名称
            model_type: 模型类型
            info: 模型信息
        """
        self.info(f"\n{'='*60}")
        self.info(f"{layer} - {model_type} 模型信息")
        self.info(f"{'='*60}")

        for key, value in info.items():
            self.info(f"{key:20s}: {value}")

        self.info(f"{'='*60}\n")


# 创建全局logger实例
system_logger = Logger('system')
layer1_logger = Logger('layer1_cornerstone')
layer2_logger = Logger('layer2_rotation')
layer3_logger = Logger('layer3_timing')


# 便捷函数
def log_info(message: str, logger_name: str = 'system'):
    """记录信息"""
    logger = Logger(logger_name)
    logger.info(message)


def log_warning(message: str, logger_name: str = 'system'):
    """记录警告"""
    logger = Logger(logger_name)
    logger.warning(message)


def log_error(message: str, logger_name: str = 'system'):
    """记录错误"""
    logger = Logger(logger_name)
    logger.error(message)
