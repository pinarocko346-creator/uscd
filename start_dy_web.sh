#!/bin/bash

# DY 选股器 Web 服务启动脚本

echo "=========================================="
echo "DY 选股器 Web 服务"
echo "=========================================="

# 检查依赖
echo "检查依赖..."
python3 -c "import flask, yfinance, pandas, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少依赖，正在安装..."
    pip3 install -r requirements.txt
fi

# 启动服务
echo "✅ 依赖检查完成"
echo "🚀 启动 Web 服务..."
echo ""
echo "访问地址: http://localhost:5001"
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

python3 dy_web_server.py
