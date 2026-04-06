#!/usr/bin/env python3
"""
FunASR对比测试脚本
用FunASR处理同一个音频文件，与Whisper的结果进行对比
"""

import os
import sys
import time
from pathlib import Path

def test_funasr():
    """使用FunASR处理音频文件"""
    
    # 查找音频文件
    import glob
    pattern = 'src/data/downloads/*6942ac7a52d4707aaa18878a*.m4a'
    matches = glob.glob(pattern)
    
    if not matches:
        print(f"❌ 错误: 找不到匹配的音频文件: {pattern}")
        return
    
    audio_file = matches[0]
    print(f"✅ 找到音频文件: {audio_file}")
    
    if not os.path.exists(audio_file):
        print(f"❌ 错误: 文件路径无效 {audio_file}")
        return
    
    print("=" * 80)
    print("🎯 FunASR 对比测试")
    print("=" * 80)
    print(f"📁 音频文件: {audio_file}")
    print(f"📊 文件大小: {os.path.getsize(audio_file) / 1024 / 1024:.2f} MB")
    print("-" * 80)
    
    try:
        # 安装FunASR（如果未安装）
        print("\n📦 检查FunASR依赖...")
        import subprocess
        result = subprocess.run(
            ["pip", "list"], 
            capture_output=True, 
            text=True
        )
        
        if "funasr" not in result.stdout.lower():
            print("⚙️  正在安装FunASR...")
            subprocess.run(
                ["pip", "install", "-U", "funasr", "modelscope"],
                check=True
            )
            print("✅ FunASR安装完成")
        else:
            print("✅ FunASR已安装")
        
        # 导入FunASR
        print("\n🔧 加载FunASR模型...")
        from funasr import AutoModel
        
        # 使用SenseVoice模型（针对中文优化）
        start_time = time.time()
        
        model = AutoModel(
            model="iic/SenseVoiceSmall",
            vad_model="fsmn-vad",      # 语音端点检测
            vad_kwargs={"max_single_segment_time": 30000},
            device="cpu"                # 根据你的硬件调整: cpu, cuda, mps
        )
        
        load_time = time.time() - start_time
        print(f"✅ 模型加载完成 (耗时: {load_time:.2f}秒)")
        
        # 开始转写
        print("\n🎙️  开始转写...")
        transcribe_start = time.time()
        
        result = model.generate(
            input=audio_file,
            language="zh",              # 中文
            use_itn=True,               # 启用文本规整
            batch_size_s=300            # 批处理大小
        )
        
        transcribe_time = time.time() - transcribe_start
        
        # 提取文本
        if isinstance(result, list):
            # 如果返回的是列表
            full_text = "\n".join([item.get("text", "") for item in result if "text" in item])
        elif isinstance(result, dict):
            # 如果返回的是字典
            full_text = result.get("text", "")
        else:
            full_text = str(result)
        
        print("✅ 转写完成！")
        print("-" * 80)
        
        # 显示结果
        print("\n📝 FunASR转写结果:")
        print("=" * 80)
        print(full_text[:1000])  # 显示前1000字符
        if len(full_text) > 1000:
            print(f"\n... (还有 {len(full_text) - 1000} 字符)")
        print("=" * 80)
        
        # 性能统计
        print("\n📊 性能统计:")
        print(f"  - 模型加载时间: {load_time:.2f}秒")
        print(f"  - 转写时间: {transcribe_time:.2f}秒")
        print(f"  - 总用时: {load_time + transcribe_time:.2f}秒")
        print(f"  - 文本长度: {len(full_text)} 字符")
        
        # 保存结果
        output_file = "funasr_comparison_result.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("FunASR SenseVoice 转写结果\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"音频文件: {audio_file}\n")
            f.write(f"转写时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"处理耗时: {transcribe_time:.2f}秒\n")
            f.write("\n" + "-" * 80 + "\n\n")
            f.write(full_text)
        
        print(f"\n?? 结果已保存到: {output_file}")
        
        # 读取原Whisper结果进行对比
        whisper_transcript = 'src/data/transcripts/xiaoyuzhou_6942ac7a52d4707aaa18878a_（14）单人独麦聊聊：不同的人对于房价波动，"受益or受损"是不同的_transcript.md'
        
        if os.path.exists(whisper_transcript):
            print("\n🔍 正在对比Whisper结果...")
            with open(whisper_transcript, "r", encoding="utf-8") as f:
                whisper_text = f.read()
            
            # 提取Whisper的转写内容（跳过元数据）
            if "## 转写内容" in whisper_text:
                whisper_content = whisper_text.split("## 转写内容")[1].strip()
            else:
                whisper_content = whisper_text
            
            print("\n📝 Whisper转写结果 (前500字符):")
            print("-" * 80)
            print(whisper_content[:500])
            print("-" * 80)
            
            print("\n📊 对比统计:")
            print(f"  - FunASR文本长度: {len(full_text)} 字符")
            print(f"  - Whisper文本长度: {len(whisper_content)} 字符")
            print(f"  - 长度差异: {abs(len(full_text) - len(whisper_content))} 字符")
        
        print("\n✅ 测试完成！")
        print("=" * 80)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装: pip install -U funasr modelscope")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_funasr()