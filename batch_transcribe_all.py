#!/usr/bin/env python3
"""
批量转写所有音频/视频文件
使用FunASR进行高精度中文识别
输出不带时间戳的Markdown文档
"""
import os
import sys
import re
import time
from pathlib import Path
from typing import List, Dict

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.logger import setup_logger

logger = setup_logger(__name__)

# 输出目录
OUTPUT_DIR = Path('data/transcripts')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_all_audio_files() -> List[Path]:
    """获取所有待处理的音频/视频文件"""
    download_dir = Path('src/data/downloads')
    
    files = []
    for ext in ['*.mp4', '*.m4a', '*.mp3', '*.wav', '*.flac']:
        files.extend(download_dir.glob(ext))
    
    return sorted(files, key=lambda x: x.name)


def clean_funasr_tags(text: str) -> str:
    """清理FunASR输出中的特殊标签"""
    # 移除语言标签 <|zh|>
    text = re.sub(r'<\|zh\|>', '', text)
    # 移除情感标签 <|NEUTRAL|> <|HAPPY|> 等
    text = re.sub(r'<\|[A-Z]+\|>', '', text)
    # 移除背景音标签 <|BGM|>
    text = re.sub(r'<\|BGM\|>', '', text)
    # 移除ITN标签 <|withitn|>
    text = re.sub(r'<\|with[a-z]+\|>', '', text)
    # 清理多余空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_title_from_filename(filename: str) -> str:
    """从文件名提取标题"""
    # 移除扩展名
    name = Path(filename).stem
    
    # B站视频：BV1234xxx_标题
    if name.startswith('BV'):
        parts = name.split('_', 1)
        if len(parts) > 1:
            return parts[1]
    
    # 小宇宙：xiaoyuzhou_id_标题
    if name.startswith('xiaoyuzhou_'):
        parts = name.split('_', 2)
        if len(parts) > 2:
            return parts[2]
    
    return name


def get_platform_from_filename(filename: str) -> str:
    """从文件名判断平台"""
    name = Path(filename).stem
    if name.startswith('BV'):
        return 'bilibili'
    elif name.startswith('xiaoyuzhou_'):
        return '小宇宙'
    else:
        return '未知'


def transcribe_file(audio_path: Path, funasr_model) -> str:
    """转写单个文件"""
    logger.info(f"正在转写: {audio_path.name}")
    
    try:
        result = funasr_model.generate(
            input=str(audio_path),
            language="zh",
            use_itn=True,
            batch_size_s=300
        )
        
        # 提取文本
        if isinstance(result, list):
            text = ' '.join([item.get('text', '') for item in result if isinstance(item, dict)])
        elif isinstance(result, dict):
            text = result.get('text', str(result))
        else:
            text = str(result)
        
        # 清理标签
        text = clean_funasr_tags(text)
        
        return text
        
    except Exception as e:
        logger.error(f"转写失败: {e}")
        return f"[转写失败: {e}]"


def format_text_to_paragraphs(text: str) -> str:
    """将文本格式化为段落"""
    # 按句号、问号、感叹号分段
    sentences = re.split(r'([。！？])', text)
    
    paragraphs = []
    current_para = []
    sentence_count = 0
    
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
        sentence = sentence.strip()
        
        if sentence:
            current_para.append(sentence)
            sentence_count += 1
        
        # 每5-8句话分一段
        if sentence_count >= 6:
            paragraphs.append(''.join(current_para))
            current_para = []
            sentence_count = 0
    
    # 添加剩余内容
    if current_para:
        paragraphs.append(''.join(current_para))
    
    return '\n\n'.join(paragraphs)


def generate_markdown(title: str, platform: str, text: str, source_file: str) -> str:
    """生成Markdown文档"""
    # 格式化文本为段落
    formatted_text = format_text_to_paragraphs(text)
    
    content = f"""# {title}

## 基本信息

- **来源平台**: {platform}
- **源文件**: {source_file}
- **转写引擎**: FunASR SenseVoice
- **生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

## 内容

{formatted_text}

---

*本文档由AI自动转写生成，可能存在少量错误，仅供参考。*
"""
    return content


def main():
    """主函数"""
    print("=" * 80)
    print("📚 批量转写所有音频/视频文件")
    print("=" * 80)
    
    # 获取所有文件
    files = get_all_audio_files()
    print(f"\n📂 找到 {len(files)} 个文件待处理")
    
    if not files:
        print("❌ 没有找到任何音频/视频文件")
        return
    
    # 显示文件列表
    print("\n待处理文件:")
    for i, f in enumerate(files, 1):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"  {i:2d}. {f.name[:60]}... ({size_mb:.1f}MB)")
    
    # 加载FunASR模型
    print("\n🔧 加载 FunASR 模型...")
    try:
        from funasr import AutoModel
        
        funasr_model = AutoModel(
            model="iic/SenseVoiceSmall",
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device="cpu"  # 使用CPU，更稳定
        )
        print("✅ 模型加载完成")
        
    except ImportError:
        print("❌ FunASR未安装，请运行: pip install -U funasr modelscope")
        return
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 开始处理
    print("\n" + "=" * 80)
    print("🚀 开始批量转写")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    total_time = 0
    
    for i, audio_file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 处理: {audio_file.name[:50]}...")
        
        # 检查是否已处理
        title = extract_title_from_filename(audio_file.name)
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:80]
        output_file = OUTPUT_DIR / f"{safe_title}.md"
        
        if output_file.exists():
            print(f"  ⏭️  已存在，跳过")
            success_count += 1
            continue
        
        start_time = time.time()
        
        try:
            # 转写
            text = transcribe_file(audio_file, funasr_model)
            
            if not text or text.startswith('[转写失败'):
                print(f"  ❌ 转写失败")
                fail_count += 1
                continue
            
            # 获取元数据
            platform = get_platform_from_filename(audio_file.name)
            
            # 生成Markdown
            markdown = generate_markdown(title, platform, text, audio_file.name)
            
            # 保存文件
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            elapsed = time.time() - start_time
            total_time += elapsed
            
            print(f"  ✅ 完成 ({elapsed:.1f}秒)")
            print(f"  📄 保存到: {output_file.name}")
            
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            fail_count += 1
    
    # 汇总
    print("\n" + "=" * 80)
    print("📊 处理完成！")
    print("=" * 80)
    print(f"  ✅ 成功: {success_count} 个")
    print(f"  ❌ 失败: {fail_count} 个")
    print(f"  ⏱️  总耗时: {total_time/60:.1f} 分钟")
    print(f"  📁 输出目录: {OUTPUT_DIR}")
    
    # 列出生成的文件
    print("\n📄 生成的文档:")
    for md_file in sorted(OUTPUT_DIR.glob('*.md')):
        print(f"  - {md_file.name}")


if __name__ == '__main__':
    main()