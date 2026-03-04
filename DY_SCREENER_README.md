# DY策略美股选股器

基于TradingView Pine Script "DY with 打点" 指标的完整Python实现。

## 功能特点

✅ **自动遍历市场**：自动获取 S&P 500 和 NASDAQ 100 成分股（600+ 只）

✅ **智能过滤**：去掉价格 < $0.1 和交易额 < $1000 万的股票

✅ **完整指标**：实现了 Pine Script 中的蓝黄带、MACD、背离信号

✅ **并发处理**：多线程加速分析

✅ **灵活配置**：支持自定义参数

## 快速开始

### 1. 安装依赖

```bash
pip install yfinance pandas numpy lxml html5lib
```

### 2. 快速测试（推荐）

```bash
python test_dy_screener.py
```

测试10只常见股票，快速验证功能是否正常。

### 3. 运行完整版

```bash
# 默认筛选所有股票
python dy_stock_screener.py

# 测试模式：只筛选前50只
python dy_stock_screener.py --max-stocks 50

# 自定义线程数
python dy_stock_screener.py --workers 20

# 指定输出文件
python dy_stock_screener.py --output my_results.csv
```

## 选股逻辑

### 1. 第一轮过滤（基本面）

- 股价 >= $0.1（去掉低价垃圾股）
- 日交易额 >= $10,000,000（去掉流动性差的股票）

### 2. 技术指标

**蓝带和黄带（趋势带）**
- 蓝带上轨 = EMA(high, 24)
- 蓝带下轨 = EMA(low, 23)
- 黄带上轨 = EMA(high, 89)
- 黄带下轨 = EMA(low, 90)

**MACD 指标**
- DIFF = EMA(close, 12) - EMA(close, 26)
- DEA = EMA(DIFF, 9)
- MACD = (DIFF - DEA) × 2

### 3. 核心信号

**买入信号（BUY）**
```
条件1: 出现底背离（LLL）
  - 价格创新低，但 MACD 的 DIFF 没有创新低
  - 说明下跌动能减弱，可能反转

条件2: DIFF 上穿 DEA（金叉）
  - DIFF 从下方穿过 DEA
  - 确认上涨趋势开始

买入信号 = 底背离 AND DIFF上穿DEA
```

**卖出信号（SELL）**
```
条件1: 出现顶背离（DBL）
  - 价格创新高，但 MACD 的 DIFF 没有创新高
  - 说明上涨动能减弱，可能回调

条件2: DIFF 下穿 DEA（死叉）
  - DIFF 从上方穿过 DEA
  - 确认下跌趋势开始

卖出信号 = 顶背离 AND DIFF下穿DEA
```

**趋势信号**
- **UP1**: 收盘价突破蓝带上轨（短期突破）
- **UP2**: 收盘价突破黄带上轨（长期突破）
- **UP3**: 蓝带下轨突破黄带上轨（强势信号）
- **DOWN1**: 收盘价跌破蓝带下轨（短期破位）
- **DOWN2**: 收盘价跌破黄带下轨（长期破位）
- **DOWN3**: 蓝带下轨跌破黄带下轨（弱势信号）

### 4. 信号优先级

```
最强信号: BUY + UP3
  → 底背离反转 + 强势突破

次强信号: BUY + UP1/UP2
  → 底背离反转 + 趋势突破

警示信号: SELL + DOWN3
  → 顶背离 + 弱势破位

观察信号: 只有UP1/UP2/UP3
  → 趋势向好，但未确认反转
```

## 输出结果

CSV文件包含以下字段：

| 字段 | 说明 |
|------|------|
| symbol | 股票代码 |
| price | 最新价格 |
| volume_usd | 日成交额（百万美元） |
| buy | 买入信号（True/False） |
| sell | 卖出信号（True/False） |
| up1/up2/up3 | 上涨趋势信号 |
| down1/down2/down3 | 下跌趋势信号 |
| diff | MACD的DIFF值 |
| dea | MACD的DEA值 |

## 实际应用建议

```python
import pandas as pd

# 读取结果
df = pd.read_csv('dy_qualified_20240304_120000.csv')

# 激进策略：只看买入信号
buy_stocks = df[df['buy'] == True]

# 稳健策略：买入信号 + 上涨趋势
strong_buy = df[(df['buy'] == True) & (df['up1'] == True)]

# 最强策略：买入信号 + 强势突破
strongest = df[(df['buy'] == True) & (df['up3'] == True)]

# 风险控制：关注卖出信号
sell_alert = df[df['sell'] == True]  # 持仓股票出现这个信号要警惕
```

## 项目结构

```
uscd/
├── utils/
│   └── dy_screener.py          # 核心选股器类
├── dy_stock_screener.py        # 主程序
├── test_dy_screener.py         # 快速测试脚本
├── DY_SCREENER_README.md       # 本文档
└── DY_QUICKSTART.md            # 快速入门指南
```

## 性能

- 单只股票分析：约0.5-1秒
- 10线程并发：约600只股票需要5-10分钟
- 建议线程数：10-20（根据网络情况调整）

## 注意事项

1. **数据源**：使用 yfinance（Yahoo Finance），免费但有速率限制
2. **网络要求**：需要稳定的网络连接
3. **API限流**：如遇到限流，减少线程数或增加延迟
4. **数据延迟**：Yahoo Finance 数据有15-20分钟延迟

## 常见问题

**Q: 为什么有些股票没有信号？**

A: 策略要求严格，只有同时满足背离+金叉/死叉才会发出买卖信号。大部分时间市场处于震荡状态，符合条件的股票较少。

**Q: 如何提高筛选速度？**

A: 增加 `--workers` 参数，但不要超过20，否则可能触发API限流。

**Q: 可以用于实盘交易吗？**

A: 本工具仅供参考，不构成投资建议。实盘交易需要结合其他分析和风险管理。

## 免责声明

本工具仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。

## License

MIT License
