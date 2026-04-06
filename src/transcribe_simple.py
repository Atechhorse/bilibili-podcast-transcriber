#!/usr/bin/env python3
"""
简化版语音转写 - 仅使用Whisper，不做说话人分离
使用CPU模式（MPS在Whisper中有兼容性问题）
但通过多线程和优化参数来加速
"""
import whisper
import torch
import os
from pathlib import Path
from datetime import timedelta
import argparse
import multiprocessing

# 设置环境变量优化CPU性能
os.environ['OMP_NUM_THREADS'] = str(min(8, multiprocessing.cpu_count()))
os.environ['MKL_NUM_THREADS'] = str(min(8, multiprocessing.cpu_count()))

def format_timestamp(seconds):
    """将秒数转换为时间戳格式"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"

def transcribe_audio(audio_path, output_dir, model_name="base"):
    """
    转写音频文件
    
    Args:
        audio_path: 音频文件路径
        output_dir: 输出目录
        model_name: Whisper模型大小 (tiny, base, small, medium, large)
    """
    audio_path = Path(audio_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成输出文件名
    output_file = output_dir / f"{audio_path.stem}_transcript.md"
    
    print(f"\n{'='*60}")
    print(f"转写文件: {audio_path.name}")
    print(f"{'='*60}")
    
    # 使用CPU模式（Whisper在MPS上有稀疏张量兼容性问题）
    device = "cpu"
    
    # 优化CPU线程数
    num_threads = min(8, multiprocessing.cpu_count())
    torch.set_num_threads(num_threads)
    
    print(f"ℹ 使用 CPU 模式（已知限制：Whisper模型在MPS上不兼容稀疏张量）")
    print(f"✓ CPU线程优化: {num_threads} 个线程")
    print(f"✓ 建议: 使用 'base' 或 'small' 模型以加快速度")
    
    # 加载模型
    print(f"\n正在加载 Whisper {model_name} 模型...")
    model = whisper.load_model(model_name, device=device)
    
    # 转写（使用优化参数）
    print("\n开始转写...")
    print(f"提示: 此过程会持续数分钟，请耐心等待...")
    
    # 使用优化的转写参数
    result = model.transcribe(
        str(audio_path),
        language="zh",  # 中文
        verbose=True,
        fp16=False,  # CPU模式禁用FP16
        # 优化参数以平衡速度和准确度
        beam_size=5,  # 默认值，适合中文
        best_of=5,    # 默认值
        temperature=0.0,  # 贪心解码，更快
        condition_on_previous_text=True  # 保持上下文连贯性
    )
    
    # 生成Markdown格式逐字稿
    print(f"\n正在生成逐字稿: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入头部信息
        f.write(f"# {audio_path.stem}\n\n")
        f.write(f"## 信息\n\n")
        f.write(f"- 源文件: {audio_path.name}\n")
        f.write(f"- 语言: 中文\n")
        f.write(f"- 模型: Whisper {model_name}\n")
        f.write(f"- 设备: {device}\n\n")
        
        f.write(f"## 逐字稿\n\n")
        
        # 写入转写内容
        for segment in result['segments']:
            timestamp = format_timestamp(segment['start'])
            text = segment['text'].strip()
            f.write(f"**{timestamp}** {text}\n\n")
    
    print(f"✓ 逐字稿已生成: {output_file}")
    print(f"  共 {len(result['segments'])} 个片段")
    
    return output_file

def main():
    parser = argparse.ArgumentParser(description='音频转写工具（简化版）')
    parser.add_argument('audio', help='音频文件路径')
    parser.add_argument('--output', '-o', default='data/transcripts', help='输出目录')
    parser.add_argument('--model', '-m', default='base', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper模型大小')
    
    args = parser.parse_args()
    
    transcribe_audio(args.audio, args.output, args.model)

if __name__ == '__main__':
    main()