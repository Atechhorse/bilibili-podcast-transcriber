#!/bin/bash

# 视频/播客处理工具启动脚本

echo "=========================================="
echo "  视频/播客音频提取与逐字稿生成工具"
echo "=========================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    exit 1
fi

# 检查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ 错误: 未找到 ffmpeg，请先安装:"
    echo "   macOS: brew install ffmpeg"
    echo "   Linux: sudo apt-get install ffmpeg"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
if [ ! -f "venv/bin/yt-dlp" ]; then
    echo "📥 安装依赖包（首次运行需要几分钟）..."
    pip install -r requirements.txt
fi

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "❌ 错误: config.yaml 不存在，请先配置"
    exit 1
fi

# 运行主程序
echo ""
echo "🚀 开始处理..."
echo ""

cd src
python main.py "$@"

echo ""
echo "✅ 处理完成！"