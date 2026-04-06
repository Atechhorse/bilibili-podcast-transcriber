#!/usr/bin/env python3
"""
基础功能测试脚本
"""
import sys
sys.path.insert(0, 'src')

from parser import LinkParser
from utils.config import load_config

def test_link_parser():
    """测试链接解析"""
    print("=" * 60)
    print("测试链接解析模块")
    print("=" * 60)
    
    parser = LinkParser()
    
    # 测试链接
    test_links = [
        "https://www.bilibili.com/video/BV14RrKBNEdH/",
        "bilibili.com/video/BV1H5qrByEAE/",
        "https://www.xiaoyuzhoufm.com/episode/69377c0c3fec3166cfff72fd",
    ]
    
    print("\n测试链接:")
    for link in test_links:
        print(f"  - {link}")
    
    # 创建临时测试文件
    with open('test_links.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(test_links))
    
    # 解析
    parsed = parser.parse_file('test_links.txt')
    
    print(f"\n✅ 解析结果: 共 {len(parsed)} 个链接\n")
    
    for i, link in enumerate(parsed, 1):
        print(f"{i}. 平台: {link['platform']}")
        print(f"   ID: {link['id']}")
        print(f"   标准化URL: {link['url']}")
        print()
    
    # 清理
    import os
    os.remove('test_links.txt')
    
    return len(parsed) == 3

def test_config():
    """测试配置加载"""
    print("=" * 60)
    print("测试配置加载")
    print("=" * 60)
    print()
    
    config = load_config('config.yaml')
    
    print(f"✅ 配置加载成功")
    print(f"   LLM Provider: {config.get('llm', {}).get('provider', 'N/A')}")
    print(f"   Whisper Model: {config.get('whisper', {}).get('model_size', 'N/A')}")
    print(f"   Whisper Device: {config.get('whisper', {}).get('device', 'N/A')}")
    print()
    
    return True

def main():
    print("\n")
    print("🚀 开始基础功能测试\n")
    
    results = []
    
    # 测试1: 配置加载
    try:
        result = test_config()
        results.append(('配置加载', result))
    except Exception as e:
        print(f"❌ 配置加载失败: {e}\n")
        results.append(('配置加载', False))
    
    # 测试2: 链接解析
    try:
        result = test_link_parser()
        results.append(('链接解析', result))
    except Exception as e:
        print(f"❌ 链接解析失败: {e}\n")
        results.append(('链接解析', False))
    
    # 汇总
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print()
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    print()
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("🎉 所有基础测试通过！")
        print()
        print("下一步:")
        print("1. 检查环境: python3 check_env.py")
        print("2. 配置 config.yaml 中的 API keys")
        print("3. 运行完整流程: cd src && python main.py")
    else:
        print("⚠️  部分测试失败，请检查错误信息")
    
    print("=" * 60)

if __name__ == '__main__':
    main()