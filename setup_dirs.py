#!/usr/bin/env python3
"""
初始化项目目录结构
"""
from pathlib import Path

def create_directories():
    """创建必要的目录"""
    dirs = [
        'data',
        'data/downloads',
        'data/temp',
        'data/transcripts',
        'logs',
        'src/utils',
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")

def main():
    print("=" * 60)
    print("  初始化项目目录结构")
    print("=" * 60)
    print()
    
    create_directories()
    
    print()
    print("✅ 目录结构创建完成！")
    print()
    print("项目结构:")
    print("  data/")
    print("    ├── downloads/      # 音频文件")
    print("    ├── temp/           # 临时文件")
    print("    └── transcripts/    # 逐字稿")
    print("  logs/                 # 日志文件")
    print("  src/                  # 源代码")
    print()

if __name__ == '__main__':
    main()