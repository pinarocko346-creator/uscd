# DY 选股器快速入门

## 1. 安装依赖

```bash
cd /Users/apple/three-layer-quant-system
pip install -r requirements.txt
```

## 2. 快速测试（推荐先运行）

使用少量股票测试功能是否正常：

```bash
python test_dy_screener.py
```

这会分析约 20 只测试股票，运行时间约 1-2 分钟。

## 3. 运行完整版本

### 方式一：使用默认参数

```bash
python dy_stock_screener.py
```

这会：
- 自动获取 S&P 500 和 NASDAQ 100 成分股（约 600 只）
- 过滤价格 < $0.1 的股票
- 过滤日交易额 < $10,000,000 的股票
- 使用 10 个并发线程
- 结果保存到 `dy_screener_results.csv`

运行时间：约 5-10 分钟（取决于网络速度）

### 方式二：自定义参数

```bash
# 提高过滤标准（只看大盘股）
python dy_stock_screener.py --min-price 10 --min-volume 100000000

# 只分析指定的股票
python dy_stock_screener.py --symbols AAPL MSFT GOOGL TSLA NVDA META AMZN

# 增加并发线程（加快速度）
python dy_stock_screener.py --workers 20

# 组合使用
python dy_stock_screener.py --min-price 5 --min-volume 50000000 --workers 15 --output my_results.csv
```

## 4. 查看结果

### 控制台输出

程序会实时显示：
- 筛选进度
- 买入信号的股票
- 卖出信号的股票
- 趋势信号统计

### CSV 文件

打开 `dy_screener_results.csv` 查看完整结果，可以用 Excel 或其他工具进一步分析。

## 5. 理解信号

### 买入信号 🟢
- 出现底背离
- MACD DIFF 上穿 DEA
- 建议关注的买入机会

### 卖出信号 🔴
- 出现顶背离
- MACD DIFF 下穿 DEA
- 建议关注的卖出机会

### 趋势信号
- **UP1**: 突破短期阻力（蓝带上轨）
- **UP2**: 突破长期阻力（黄带上轨）
- **UP3**: 强势信号（蓝带突破黄带）
- **DOWN1**: 跌破短期支撑（蓝带下轨）
- **DOWN2**: 跌破长期支撑（黄带下轨）
- **DOWN3**: 弱势信号（蓝带跌破黄带）

## 6. 常见问题

### Q: 运行很慢怎么办？
A: 可以增加并发线程数：`--workers 20`

### Q: 想只看某些股票怎么办？
A: 使用 `--symbols` 参数指定股票列表

### Q: 如何获取更多股票？
A: 修改 `utils/dy_screener.py` 中的 `get_us_stock_list()` 函数

### Q: 数据从哪里来？
A: 使用 yfinance 从 Yahoo Finance 获取免费数据

### Q: 可以用于实盘交易吗？
A: 本工具仅供参考，不构成投资建议。实盘交易需要更多验证和风险管理。

## 7. 下一步

1. 分析历史回测表现
2. 结合其他指标（如成交量、RSI 等）
3. 添加止损止盈逻辑
4. 集成到现有的量化系统中

## 8. 与原 Pine Script 的区别

| 特性 | Pine Script | Python 版本 |
|-----|------------|-----------|
| 股票数量 | 硬编码 40 只 | 自动获取 600+ 只 |
| 过滤条件 | 无 | 价格和交易量过滤 |
| 运行环境 | TradingView | 本地 Python |
| 数据更新 | 实时 | 延迟（免费数据） |
| 扩展性 | 受限 | 完全可定制 |
| 批量处理 | 不支持 | 支持并发处理 |

## 9. 示例工作流

```bash
# 1. 先测试
python test_dy_screener.py

# 2. 运行完整筛选
python dy_stock_screener.py --min-price 1 --min-volume 20000000

# 3. 查看结果
cat dy_screener_results.csv | grep "True" | head -20

# 4. 针对特定股票深入分析
python dy_stock_screener.py --symbols AAPL MSFT GOOGL
```

## 10. 技术支持

详细文档请参考：[DY_SCREENER_README.md](DY_SCREENER_README.md)
