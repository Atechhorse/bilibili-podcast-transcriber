#!/usr/bin/env python3
"""
环境检查脚本
"""
import sys
import subprocess
import importlib.util

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 9:
        print("✅ Python 版本满足要求 (>= 3.9)")
        return True
    else:
        print("❌ Python 版本过低，需要 >= 3.9")
        return False

def check_command(cmd):
    """检查命令是否存在"""
    try:
        result = subprocess.run(
            [cmd, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False

def check_package(package_name, import_name=None):
    """检查 Python 包是否已安装"""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def main():
    print("=" * 60)
    print("  环境检查")
    print("=" * 60)
    print()
    
    all_ok = True
    
    # 1. Python 版本
    print("1️⃣  检查 Python 版本")
    if not check_python_version():
        all_ok = False
    print()
    
    # 2. 系统命令
    print("2️⃣  检查系统命令")
    
    if check_command('ffmpeg'):
        print("✅ ffmpeg 已安装")
    else:
        print("❌ ffmpeg 未安装")
        print("   macOS: brew install ffmpeg")
        print("   Linux: sudo apt-get install ffmpeg")
        all_ok = False
    print()
    
    # 3. Python 包
    print("3️⃣  检查 Python 依赖包")
    
    packages = [
        ('whisper', 'whisper'),
        ('pyannote.audio', 'pyannote.audio'),
        ('torch', 'torch'),
        ('yt-dlp', 'yt_dlp'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('pyyaml', 'yaml'),
        ('ffmpeg-python', 'ffmpeg'),
    ]
    
    missing_packages = []
    
    for pkg_name, import_name in packages:
        if check_package(pkg_name, import_name):
            print(f"✅ {pkg_name}")
        else:
            print(f"❌ {pkg_name}")
            missing_packages.append(pkg_name)
    
    if missing_packages:
        print()
        print("缺少依赖包，请运行:")
        print("  pip install -r requirements.txt")
        all_ok = False
    print()
    
    # 4. 配置文件
    print("4️⃣  检查配置文件")
    
    try:
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("✅ config.yaml 存在")
        
        # 检查关键配置
        if config.get('llm', {}).get('api_key'):
            print("✅ LLM API Key 已配置")
        else:
            print("⚠️  LLM API Key 未配置（说话人识别将受限）")
        
        if config.get('huggingface_token'):
            print("✅ HuggingFace Token 已配置")
        else:
            print("⚠️  HuggingFace Token 未配置（说话人分离将跳过）")
    
    except FileNotFoundError:
        print("❌ config.yaml 不存在")
        all_ok = False
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        all_ok = False
    
    print()
    
    # 5. 硬件加速
    print("5️⃣  检查硬件加速支持")
    
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA 可用 (GPU: {torch.cuda.get_device_name(0)})")
        elif torch.backends.mps.is_available():
            print("✅ MPS 可用 (Apple Silicon)")
        else:
            print("⚠️  仅 CPU 可用（处理速度会较慢）")
    except:
        print("⚠️  无法检测硬件加速")
    
    print()
    print("=" * 60)
    
    if all_ok:
        print("✅ 环境检查通过！可以开始使用。")
        print()
        print("快速开始:")
        print("  cd src")
        print("  python main.py")
    else:
        print("❌ 环境检查未通过，请先解决上述问题。")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
