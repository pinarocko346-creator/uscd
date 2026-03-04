# DY策略选股器 - 快速入门

## 5分钟上手指南

### 第一步：安装依赖

```bash
pip install yfinance pandas numpy lxml html5lib
```

### 第二步：快速测试

```bash
python test_dy_screener.py
```

这会测试10只常见股票（AAPL, MSFT, GOOGL等），大约需要10-20秒。

**预期输出：**
```
============================================================
DY策略选股器 - 快速测试
============================================================

测试 10 只股票...
------------------------------------------------------------

[1/10] 正在分析 AAPL...
  ✗ 无信号或不符合条件

[2/10] 正在分析 MSFT...
  ✓ 有信号: DOWN1
  价格: $420.50
  成交额: $2500.00M
  DIFF: -0.5000, DEA: 0.2000

...

============================================================
测试完成！
入选: 3/10 只
耗时: 15.23 秒
============================================================
```

### 第三步：运行完整版

```bash
# 测试模式：只筛选前50只股票
python dy_stock_screener.py --max-stocks 50

# 完整模式：筛选所有600+只股票（需要5-10分钟）
python dy_stock_screener.py
```

### 第四步：查看结果

程序会生成CSV文件，例如 `dy_qualified_20240304_120000.csv`

用Excel或Python打开：

```python
import pandas as pd

df = pd.read_csv('dy_qualified_20240304_120000.csv')

# 查看买入信号的股票
buy_stocks = df[df['buy'] == True]
print(buy_stocks[['symbol', 'price', 'buy', 'up1', 'up2', 'up3']])
```

## 信号解读

### 买入信号（BUY）

**含义**：底背离 + MACD金叉

**操作建议**：
- 如果同时有 UP1/UP2/UP3，信号更强
- 建议等待回调后再入场
- 设置止损在最近低点下方

### 卖出信号（SELL）

**含义**：顶背离 + MACD死叉

**操作建议**：
- 如果持有该股票，考虑减仓或止盈
- 如果同时有 DOWN1/DOWN2/DOWN3，下跌风险更大

### 趋势信号

| 信号 | 含义 | 强度 |
|------|------|------|
| UP1 | 突破短期阻力 | ⭐⭐ |
| UP2 | 突破长期阻力 | ⭐⭐⭐ |
| UP3 | 强势突破 | ⭐⭐⭐⭐⭐ |
| DOWN1 | 跌破短期支撑 | ⚠️⚠️ |
| DOWN2 | 跌破长期支撑 | ⚠️⚠️⚠️ |
| DOWN3 | 弱势破位 | ⚠️⚠️⚠️⚠️⚠️ |

## 实战策略

### 激进策略

```python
# 只要有买入信号就关注
buy_stocks = df[df['buy'] == True]
```

### 稳健策略

```python
# 买入信号 + 上涨趋势
strong_buy = df[(df['buy'] == True) & (df['up1'] == True)]
```

### 最强策略

```python
# 买入信号 + 强势突破
strongest = df[(df['buy'] == True) & (df['up3'] == True)]
```

### 风险控制

```python
# 持仓股票出现卖出信号，考虑止盈
sell_alert = df[df['sell'] == True]
```

## 常用命令

```bash
# 快速测试
python test_dy_screener.py

# 测试50只股票
python dy_stock_screener.py --max-stocks 50

# 完整筛选（600+只）
python dy_stock_screener.py

# 使用20个线程加速
python dy_stock_screener.py --workers 20

# 指定输出文件名
python dy_stock_screener.py --output my_results.csv
```

## 下一步

1. 阅读 [DY_SCREENER_README.md](DY_SCREENER_README.md) 了解详细逻辑
2. 根据自己的风险偏好调整筛选条件
3. 结合其他分析工具（基本面、资金流等）
4. 建立自己的交易系统和风险管理规则

## 获取帮助

```bash
python dy_stock_screener.py --help
```

## 免责声明

本工具仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。
