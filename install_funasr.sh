#!/bin/bash
# FunASR 依赖安装脚本

echo "======================================"
echo "安装 FunASR 及相关依赖"
echo "======================================"

# 安装FunASR
echo ""
echo "步骤 1/3: 安装 FunASR..."
pip install -U funasr modelscope

# 安装音频处理库
echo ""
echo "步骤 2/3: 安装音频处理库..."
pip install -U librosa soundfile

# 验证安装
echo ""
echo "步骤 3/3: 验证安装..."
python3 << 'EOF'
try:
    import funasr
    print("✓ FunASR 安装成功")
    print(f"  版本: {funasr.__version__ if hasattr(funasr, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"✗ FunASR 安装失败: {e}")

try:
    import modelscope
    print("✓ ModelScope 安装成功")
except ImportError as e:
    print(f"✗ ModelScope 安装失败: {e}")

try:
    import librosa
    print("✓ librosa 安装成功")
except ImportError as e:
    print(f"✗ librosa 安装失败: {e}")

try:
    import soundfile
    print("✓ soundfile 安装成功")
except ImportError as e:
    print(f"✗ soundfile 安装失败: {e}")
EOF

echo ""
echo "======================================"
echo "安装完成！"
echo "======================================"
echo ""
echo "使用方法："
echo "  1. 修改 config.yaml，设置 asr_engine: \"funasr\""
echo "  2. 运行测试: python test_funasr_integration.py"
echo "  3. 运行主程序: python src/main.py"
echo ""