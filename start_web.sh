#!/bin/bash

# 三层量化系统 - Web界面启动脚本

echo "========================================"
echo "三层量化策略系统 - Web界面"
echo "========================================"
echo ""

# 检查Python
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到Python"
    exit 1
fi

echo "✓ Python已安装"

# 检查Flask
python -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Flask未安装"
    echo ""
    echo "正在安装Flask..."
    pip install Flask
    if [ $? -ne 0 ]; then
        echo "❌ Flask安装失败"
        exit 1
    fi
fi

echo "✓ Flask已安装"
echo ""
echo "========================================"
echo "启动Web服务器..."
echo "========================================"
echo ""
echo "访问地址: http://localhost:8080"
echo "或者: http://127.0.0.1:8080"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python web_server.py
