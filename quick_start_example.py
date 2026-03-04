"""
三层量化系统 - 快速开始示例
展示如何使用系统的基本流程
"""

# ============================================================================
# 示例1：第一层基石层 - 多因子选股
# ============================================================================

def example_layer1():
    """第一层：基石层示例"""
    print("=" * 80)
    print("第一层：基石层 - 多因子选股")
    print("=" * 80)

    # 步骤1：获取数据
    print("\n[步骤1] 获取沪深300成分股数据...")
    # universe = get_index_stocks("000300.XSHG", "2026-03-03")
    # 示例：假设有300只股票
    universe = [f"00000{i}.XSHE" for i in range(1, 301)]
    print(f"  获取到 {len(universe)} 只股票")

    # 步骤2：计算因子
    print("\n[步骤2] 计算5个因子...")
    factors = {
        'PE': "市盈率（越低越好）",
        'PB': "市净率（越低越好）",
        'ROE': "净资产收益率（越高越好）",
        'GrossMargin': "毛利率（越高越好）",
        'Momentum': "20日涨跌幅（适度动量）"
    }
    for factor, desc in factors.items():
        print(f"  - {factor}: {desc}")

    # 步骤3：因子标准化
    print("\n[步骤3] 因子标准化（Z-Score）...")
    print("  - 去极值（Winsorize 1%-99%）")
    print("  - Z-Score标准化")
    print("  - 方向调整（价值因子取负）")

    # 步骤4：计算综合得分
    print("\n[步骤4] 计算综合得分...")
    weights = {
        'PE': 0.25,
        'PB': 0.25,
        'ROE': 0.20,
        'GrossMargin': 0.15,
        'Momentum': 0.15
    }
    print("  因子权重:")
    for factor, weight in weights.items():
        print(f"    {factor}: {weight*100:.0f}%")

    # 步骤5：选股
    print("\n[步骤5] 选出前20只股票...")
    selected = [
        "000001.XSHE", "000002.XSHE", "000333.XSHE", "000651.XSHE",
        "000858.XSHE", "600000.XSHG", "600036.XSHG", "600519.XSHG",
        # ... 省略其他12只
    ]
    print(f"  选中 {len(selected)} 只股票")
    for i, stock in enumerate(selected[:5], 1):
        print(f"    {i}. {stock}")
    print("    ...")

    # 步骤6：仓位分配
    print("\n[步骤6] 仓位分配...")
    print(f"  总仓位: 50%")
    print(f"  每只股票: 2.5%")
    print(f"  剩余现金: 50%")

    # 步骤7：风险控制
    print("\n[步骤7] 风险控制设置...")
    print("  - 单股止损: -15%")
    print("  - 组合回撤: -20%")
    print("  - 连续跑输: 2个月")

    print("\n[完成] 下次调仓: 下月第一个交易日")
    print("=" * 80)


# ============================================================================
# 示例2：第二层轮动层 - 随机森林
# ============================================================================

def example_layer2():
    """第二层：轮动层示例"""
    print("\n" + "=" * 80)
    print("第二层：轮动层 - 随机森林动态因子")
    print("=" * 80)

    # 步骤1：计算IC值
    print("\n[步骤1] 计算8个候选因子的IC值...")
    candidate_factors = [
        "PE", "PB", "PS", "ROE", "ROA",
        "GrossMargin", "Momentum_20", "Momentum_60"
    ]
    ic_values = {
        "PE": 0.15,
        "PB": 0.12,
        "ROE": 0.18,
        "GrossMargin": 0.14,
        "Momentum_20": 0.16,
        "PS": 0.10,
        "ROA": 0.13,
        "Momentum_60": 0.11
    }

    print("  IC值排名:")
    sorted_ic = sorted(ic_values.items(), key=lambda x: x[1], reverse=True)
    for i, (factor, ic) in enumerate(sorted_ic, 1):
        print(f"    {i}. {factor}: {ic:.3f}")

    # 步骤2：选出黄金因子
    print("\n[步骤2] 选出IC值最高的5个黄金因子...")
    golden_factors = [f[0] for f in sorted_ic[:5]]
    print(f"  本周黄金因子: {golden_factors}")

    # 步骤3：训练随机森林
    print("\n[步骤3] 训练随机森林模型...")
    print("  - 训练数据: 过去120天")
    print("  - 树的数量: 100")
    print("  - 最大深度: 5")
    print("  - 模型R²: 0.65 ✓")

    # 步骤4：预测与选股
    print("\n[步骤4] 预测未来5日收益...")
    print("  选出预测收益最高的15只股票")
    selected = [f"00{i:04d}.XSHE" for i in range(1, 16)]
    for i, stock in enumerate(selected[:5], 1):
        print(f"    {i}. {stock} - 预测收益: +3.2%")
    print("    ...")

    # 步骤5：协同检查
    print("\n[步骤5] 与基石层协同检查...")
    print("  - 重叠股票: 2只")
    print("  - 风格趋同: 正常 ✓")

    # 步骤6：调仓
    print("\n[步骤6] 调仓计划（下周一执行）...")
    print("  - 卖出: 8只")
    print("  - 买入: 8只")
    print("  - 保持: 7只")
    print("  - 换手率: 53% ✓")

    print("\n[完成] 下次计算: 本周五收盘后")
    print("=" * 80)


# ============================================================================
# 示例3：第三层择时层 - 三模型投票
# ============================================================================

def example_layer3():
    """第三层：择时层示例"""
    print("\n" + "=" * 80)
    print("第三层：择时层 - KNN+SVM+NLP三模型投票")
    print("=" * 80)

    # 模型1：KNN
    print("\n[模型1] KNN历史相似度...")
    print("  - 今日特征: [0.5%, -0.3%, 1.2%, ...]")
    print("  - 找到最相似的5天:")
    print("    2025-12-15: 次日 +1.5%")
    print("    2025-10-08: 次日 +0.8%")
    print("    2025-08-22: 次日 +1.2%")
    print("    2025-06-10: 次日 -0.5%")
    print("    2025-04-03: 次日 +0.9%")
    print("  - 上涨概率: 80% (4/5)")
    print("  - KNN投票: 看多 ✓")

    # 模型2：SVM
    print("\n[模型2] SVM技术指标分类...")
    print("  - RSI: 45 (中性)")
    print("  - MACD: 正值且上升")
    print("  - 布林带: 中轨附近")
    print("  - 均线: 多头排列")
    print("  - SVM预测: 上涨")
    print("  - SVM投票: 看多 ✓")

    # 模型3：NLP
    print("\n[模型3] NLP市场情绪...")
    print("  - 抓取评论: 1250条")
    print("  - 情绪分布:")
    print("    乐观: 45%")
    print("    中性: 35%")
    print("    悲观: 20%")
    print("  - 情绪得分: +0.25 (偏乐观)")
    print("  - NLP投票: 看多 ✓")

    # 投票结果
    print("\n[投票结果] 3票看多")
    print("  决策: 满仓ETF (20%)")
    print("  标的: 沪深300ETF (510300)")

    # 执行
    print("\n[执行计划] 明日09:30...")
    print("  - 买入: 510300")
    print("  - 仓位: 20%")
    print("  - 止损: -3%")

    print("\n[完成] 下次计算: 明日收盘后")
    print("=" * 80)


# ============================================================================
# 示例4：完整系统运行
# ============================================================================

def example_full_system():
    """完整系统示例"""
    print("\n" + "=" * 80)
    print("完整系统运行示例")
    print("=" * 80)

    print("\n[日期] 2026-03-03 (周一)")

    # 检查各层调仓时间
    print("\n[调仓检查]")
    print("  第一层: 不调仓（每月第一个交易日）")
    print("  第二层: 调仓 ✓（每周一）")
    print("  第三层: 调仓 ✓（每日）")

    # 当前持仓
    print("\n[当前持仓]")
    print("  第一层（50%）:")
    print("    20只沪深300股票 × 2.5%")
    print("  第二层（30%）:")
    print("    15只中证500股票 × 2%")
    print("  第三层（20%）:")
    print("    沪深300ETF × 20%")
    print("  现金: 0%")

    # 执行调仓
    print("\n[执行调仓]")
    print("  第二层:")
    print("    - 卖出8只，买入8只")
    print("    - 换手率: 53%")
    print("  第三层:")
    print("    - 保持满仓ETF")

    # 风险检查
    print("\n[风险检查]")
    print("  - 单股最大亏损: -8.5% ✓")
    print("  - 组合回撤: -12.3% ✓")
    print("  - 模型R²: 0.65 ✓")
    print("  - 所有风险指标正常")

    # 性能统计
    print("\n[性能统计]")
    print("  - 今日收益: +1.2%")
    print("  - 本周收益: +2.5%")
    print("  - 本月收益: +3.8%")
    print("  - 年化收益: 18.5%")
    print("  - 夏普比率: 1.65")
    print("  - 最大回撤: -15.2%")

    print("\n[完成] 系统运行正常")
    print("=" * 80)


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""
    print("\n" + "=" * 80)
    print("三层量化系统 - 快速开始示例")
    print("=" * 80)

    print("\n本示例展示系统的基本使用流程")
    print("实际使用时，需要连接真实数据源")

    # 运行各层示例
    example_layer1()
    example_layer2()
    example_layer3()
    example_full_system()

    print("\n" + "=" * 80)
    print("示例完成！")
    print("=" * 80)
    print("\n下一步:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 配置数据源: 编辑 config/system_config.py")
    print("3. 运行回测: python backtest.py")
    print("4. 实盘运行: python main.py")


if __name__ == "__main__":
    main()
