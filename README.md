# DY策略美股选股器

基于TradingView Pine Script "DY with 打点" 指标的完整Python实现。

## 功能特点

- ✅ 自动遍历 S&P 500 和 NASDAQ 100（600+ 只股票）
- ✅ 智能过滤低价股和低流动性股票
- ✅ 完整实现蓝黄带、MACD、背离信号
- ✅ 多线程并发处理
- ✅ 支持命令行参数

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 快速测试
python test_dy_screener.py

# 3. 运行完整版
python dy_stock_screener.py
```

## 文档

- [详细文档](DY_SCREENER_README.md) - 完整的选股逻辑和使用说明
- [快速入门](DY_QUICKSTART.md) - 5分钟上手指南

## 选股逻辑

### 买入信号（BUY）
底背离 + MACD金叉 → 可能反转向上

### 卖出信号（SELL）
顶背离 + MACD死叉 → 可能反转向下

### 趋势信号
- UP1/UP2/UP3：上涨趋势
- DOWN1/DOWN2/DOWN3：下跌趋势

## 输出示例

```csv
symbol,price,volume_usd,buy,sell,up1,up2,up3,down1,down2,down3,diff,dea
AAPL,175.50,5000.00,True,False,True,False,False,False,False,False,1.2345,0.9876
MSFT,420.30,3500.00,False,False,False,True,False,False,False,False,0.5678,0.4321
```

## 免责声明

本工具仅供学习和研究使用，不构成任何投资建议。股市有风险，投资需谨慎。

## License

MIT License
