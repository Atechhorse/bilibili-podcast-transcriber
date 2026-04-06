#!/usr/bin/env python3
"""
批量音频转写工具
处理整个目录下的所有音频文件
"""
import sys
from pathlib import Path
import time
from transcribe_simple import transcribe_audio

def batch_transcribe(audio_dir, output_dir, model_name="base", file_patterns=None):
    """
    批量转写音频文件
    
    Args:
        audio_dir: 音频文件目录
        output_dir: 输出目录
        model_name: Whisper模型大小
        file_patterns: 文件模式列表，如 ['*.mp4', '*.m4a']
    """
    audio_dir = Path(audio_dir)
    output_dir = Path(output_dir)
    
    if file_patterns is None:
        file_patterns = ['*.mp4', '*.m4a', '*.mp3', '*.wav']
    
    # 收集所有音频文件
    audio_files = []
    for pattern in file_patterns:
        audio_files.extend(audio_dir.glob(pattern))
    
    audio_files = sorted(audio_files, key=lambda x: x.stat().st_size)  # 从小到大排序
    
    if not audio_files:
        print(f"❌ 在 {audio_dir} 中没有找到音频文件")
        return
    
    print("="*70)
    print(f"批量转写任务")
    print("="*70)
    print(f"📁 音频目录: {audio_dir}")
    print(f"📁 输出目录: {output_dir}")
    print(f"🎯 模型: Whisper {model_name}")
    print(f"📊 文件总数: {len(audio_files)} 个")
    print(f"💾 总大小: {sum(f.stat().st_size for f in audio_files) / (1024**3):.2f} GB")
    print("="*70)
    
    # 检查已完成的文件
    completed = []
    for audio_file in audio_files:
        transcript_file = output_dir / f"{audio_file.stem}_transcript.md"
        if transcript_file.exists():
            completed.append(audio_file)
    
    if completed:
        print(f"\n✓ 已完成 {len(completed)}/{len(audio_files)} 个文件")
        print(f"  剩余 {len(audio_files) - len(completed)} 个待处理")
        
        response = input("\n是否跳过已完成的文件？(Y/n): ")
        if response.lower() != 'n':
            audio_files = [f for f in audio_files if f not in completed]
    
    if not audio_files:
        print("\n✅ 所有文件都已转写完成！")
        return
    
    # 预估时间
    total_minutes = sum(f.stat().st_size / (1024**2) for f in audio_files) * 0.5  # 假设每MB约0.5分钟
    print(f"\n⏱️  预计总耗时: {total_minutes:.0f} 分钟 (约 {total_minutes/60:.1f} 小时)")
    print(f"💡 提示: 可以随时按 Ctrl+C 中断，下次会自动跳过已完成的文件")
    
    input("\n按 Enter 开始转写...")
    
    # 开始批量转写
    start_time = time.time()
    success_count = 0
    failed_files = []
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n{'='*70}")
        print(f"处理进度: [{i}/{len(audio_files)}]")
        print(f"当前文件: {audio_file.name}")
        print(f"文件大小: {audio_file.stat().st_size / (1024**2):.1f} MB")
        print(f"{'='*70}")
        
        try:
            file_start = time.time()
            transcribe_audio(str(audio_file), str(output_dir), model_name)
            file_elapsed = time.time() - file_start
            
            success_count += 1
            print(f"\n✅ 完成! 耗时: {file_elapsed/60:.1f} 分钟")
            
            # 显示剩余预估时间
            if i < len(audio_files):
                avg_time_per_file = (time.time() - start_time) / i
                remaining_time = avg_time_per_file * (len(audio_files) - i)
                print(f"📊 预计剩余时间: {remaining_time/60:.0f} 分钟")
                
        except KeyboardInterrupt:
            print("\n\n⚠️ 用户中断！")
            print(f"已完成: {success_count}/{len(audio_files)} 个文件")
            print("下次运行会自动跳过已完成的文件。")
            sys.exit(0)
            
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            failed_files.append((audio_file.name, str(e)))
            continue
    
    # 最终统计
    total_elapsed = time.time() - start_time
    print("\n" + "="*70)
    print("批量转写完成！")
    print("="*70)
    print(f"✅ 成功: {success_count} 个")
    print(f"❌ 失败: {len(failed_files)} 个")
    print(f"⏱️  总耗时: {total_elapsed/60:.1f} 分钟 ({total_elapsed/3600:.2f} 小时)")
    
    if failed_files:
        print(f"\n失败文件列表:")
        for filename, error in failed_files:
            print(f"  - {filename}: {error}")
    
    print(f"\n📁 逐字稿保存在: {output_dir}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='批量音频转写工具')
    parser.add_argument('--audio-dir', default='src/data/downloads', help='音频文件目录')
    parser.add_argument('--output', '-o', default='src/data/transcripts', help='输出目录')
    parser.add_argument('--model', '-m', default='base', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       help='Whisper模型大小')
    
    args = parser.parse_args()
    
    batch_transcribe(args.audio_dir, args.output, args.model)

if __name__ == '__main__':
    main()