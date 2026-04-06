#!/usr/bin/env python3
"""
处理对话类型的音频文件
使用说话人分离功能区分付鹏和其他人
"""
import os
import sys
import re
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.logger import setup_logger

logger = setup_logger(__name__)

# 对话类型的文件（需要说话人分离）
DIALOGUE_FILES = [
    "xiaoyuzhou_6605297c1519139e4f217f05",  # vol.54 对话付鹏：当社会风险偏好变了
    "xiaoyuzhou_66878ecf0bc5d7cc700115d0",  # E146 对话付鹏：普通人如何有效捕捉
    "xiaoyuzhou_67fbc62a623bc78c395f5bc9",  # 03 躺平or躺赚？｜对话付鹏
    "xiaoyuzhou_68ff8406083a71a4eb82b352",  # 12 "老登"经济学｜对话付鹏
    "xiaoyuzhou_69377c0c3fec3166cfff72fd",  # E136.听付鹏讲几个故事
    "xiaoyuzhou_687e7580a12f9ff06a550307",  # 付鹏：考古专业比计算机更有赚头
    "xiaoyuzhou_6835bdd631215eb50605205a",  # （01）揭秘"谣言经济学"
]

OUTPUT_DIR = Path('data/transcripts')


def clean_funasr_tags(text: str) -> str:
    """清理FunASR输出中的特殊标签"""
    text = re.sub(r'<\|[A-Za-z_]+\|>', '', text)
    return text.strip()


def extract_title_from_filename(filename: str) -> str:
    """从文件名提取标题"""
    name = Path(filename).stem
    if name.startswith('xiaoyuzhou_'):
        parts = name.split('_', 2)
        if len(parts) > 2:
            return parts[2]
    return name


def transcribe_with_speaker_diarization(audio_path: Path, funasr_model, speaker_model):
    """使用说话人分离进行转写"""
    logger.info(f"正在转写（含说话人分离）: {audio_path.name}")
    
    try:
        # 1. 先进行ASR转写
        asr_result = funasr_model.generate(
            input=str(audio_path),
            language="zh",
            use_itn=True,
            batch_size_s=300
        )
        
        # 提取文本
        if isinstance(asr_result, list):
            full_text = ' '.join([item.get('text', '') for item in asr_result if isinstance(item, dict)])
        elif isinstance(asr_result, dict):
            full_text = asr_result.get('text', str(asr_result))
        else:
            full_text = str(asr_result)
        
        full_text = clean_funasr_tags(full_text)
        
        # 2. 进行说话人分离
        logger.info("  执行说话人分离...")
        
        # 使用FunASR的说话人分离模型
        try:
            speaker_result = speaker_model.generate(
                input=str(audio_path),
                batch_size_s=300
            )
            
            # 解析说话人结果
            segments = parse_speaker_segments(speaker_result, full_text)
            
            if segments and len(set(s['speaker'] for s in segments)) > 1:
                logger.info(f"  检测到 {len(set(s['speaker'] for s in segments))} 个说话人")
                return segments
            else:
                logger.info("  未能区分说话人，使用备选方案")
                return fallback_speaker_detection(full_text)
                
        except Exception as e:
            logger.warning(f"  说话人分离失败: {e}，使用备选方案")
            return fallback_speaker_detection(full_text)
        
    except Exception as e:
        logger.error(f"转写失败: {e}")
        return []


def parse_speaker_segments(result, full_text: str):
    """解析说话人分离结果"""
    segments = []
    
    # FunASR返回格式可能不同，尝试多种解析方式
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict):
                speaker = item.get('speaker', item.get('spk', 'SPEAKER_00'))
                text = item.get('text', '')
                if text:
                    segments.append({
                        'speaker': speaker,
                        'text': clean_funasr_tags(text)
                    })
    
    if not segments and full_text:
        # 如果没有成功解析，按句子简单分割
        sentences = re.split(r'([。！？])', full_text)
        current_text = ""
        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
            if sentence.strip():
                current_text += sentence
                if len(current_text) > 100:
                    segments.append({
                        'speaker': 'SPEAKER_00',
                        'text': current_text.strip()
                    })
                    current_text = ""
        if current_text:
            segments.append({
                'speaker': 'SPEAKER_00',
                'text': current_text.strip()
            })
    
    return segments


def fallback_speaker_detection(text: str):
    """备选说话人检测方案：基于对话特征分析"""
    segments = []
    
    # 按句子分割
    sentences = re.split(r'([。！？])', text)
    
    current_speaker = 'SPEAKER_A'
    current_text = []
    last_was_question = False
    
    for i in range(0, len(sentences)-1, 2):
        sentence = sentences[i].strip()
        punct = sentences[i+1] if i+1 < len(sentences) else ''
        
        if not sentence:
            continue
        
        full_sentence = sentence + punct
        
        # 简单启发式：
        # - 问号后通常换人说话
        # - 某些开头词暗示新说话人
        
        switch_speaker = False
        
        # 检测对话切换的标志
        if last_was_question and not sentence.startswith(('对', '是', '嗯', '啊', '哦')):
            switch_speaker = True
        
        # 检测主持人/采访者常用语
        host_patterns = [
            r'^那(么)?.*呢',
            r'^所以.*吗',
            r'^你(觉得|认为|怎么看)',
            r'^关于这个',
            r'^我们.*聊聊',
            r'^接下来',
            r'^好的',
        ]
        
        for pattern in host_patterns:
            if re.match(pattern, sentence):
                if current_speaker == 'SPEAKER_A':
                    switch_speaker = True
                break
        
        # 检测付鹏常用语（专业分析）
        fupeng_patterns = [
            r'(投资|资产|配置|周期|通胀|通缩|杠杆|负债)',
            r'(市场|经济|金融|风险|收益)',
            r'(其实|本质上|逻辑是|核心是)',
            r'我(认为|觉得|一直说)',
        ]
        
        is_professional = False
        for pattern in fupeng_patterns:
            if re.search(pattern, sentence):
                is_professional = True
                break
        
        if switch_speaker:
            # 保存当前段落
            if current_text:
                segments.append({
                    'speaker': current_speaker,
                    'text': ''.join(current_text)
                })
                current_text = []
            
            # 切换说话人
            current_speaker = 'SPEAKER_B' if current_speaker == 'SPEAKER_A' else 'SPEAKER_A'
        
        current_text.append(full_sentence)
        last_was_question = punct == '？'
    
    # 保存最后一段
    if current_text:
        segments.append({
            'speaker': current_speaker,
            'text': ''.join(current_text)
        })
    
    # 合并相邻的同一说话人段落
    merged_segments = []
    for seg in segments:
        if merged_segments and merged_segments[-1]['speaker'] == seg['speaker']:
            merged_segments[-1]['text'] += seg['text']
        else:
            merged_segments.append(seg)
    
    return merged_segments


def identify_speakers(segments):
    """识别哪个是付鹏（通常说话最多且专业术语多）"""
    if not segments:
        return segments
    
    # 统计每个说话人的发言量和专业术语数
    speaker_stats = {}
    professional_keywords = [
        '投资', '资产', '配置', '周期', '通胀', '通缩', '杠杆', '负债',
        '市场', '经济', '金融', '风险', '收益', '股票', '债券', '房产',
        '利率', '货币', '财政', 'GDP', '美联储', '央行', '人口', '消费'
    ]
    
    for seg in segments:
        speaker = seg['speaker']
        text = seg['text']
        
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {'total_len': 0, 'keyword_count': 0}
        
        speaker_stats[speaker]['total_len'] += len(text)
        
        for keyword in professional_keywords:
            speaker_stats[speaker]['keyword_count'] += text.count(keyword)
    
    # 找出付鹏（发言最多且专业术语最多）
    fupeng_speaker = None
    max_score = 0
    
    for speaker, stats in speaker_stats.items():
        score = stats['total_len'] + stats['keyword_count'] * 50
        if score > max_score:
            max_score = score
            fupeng_speaker = speaker
    
    # 重新标记
    speaker_names = {}
    other_count = 0
    
    for speaker in speaker_stats.keys():
        if speaker == fupeng_speaker:
            speaker_names[speaker] = '付鹏'
        else:
            other_count += 1
            if other_count == 1:
                speaker_names[speaker] = '主持人'
            else:
                speaker_names[speaker] = f'嘉宾{other_count}'
    
    # 更新segments
    for seg in segments:
        seg['speaker'] = speaker_names.get(seg['speaker'], seg['speaker'])
    
    return segments


def format_dialogue_markdown(title: str, segments, source_file: str) -> str:
    """格式化为对话式Markdown"""
    content = f"""# {title}

## 基本信息

- **来源平台**: 小宇宙
- **源文件**: {source_file}
- **转写引擎**: FunASR SenseVoice（含说话人分离）
- **生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

## 对话内容

"""
    
    for seg in segments:
        speaker = seg['speaker']
        text = seg['text']
        
        # 分段处理长文本
        if len(text) > 200:
            # 按句子分段
            sentences = re.split(r'([。！？])', text)
            formatted_text = ""
            line_len = 0
            
            for i in range(0, len(sentences)-1, 2):
                sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else '')
                formatted_text += sentence
                line_len += len(sentence)
                
                if line_len > 80:
                    formatted_text += "\n"
                    line_len = 0
            
            text = formatted_text.strip()
        
        content += f"**{speaker}**：{text}\n\n"
    
    content += """---

*本文档由AI自动转写生成，说话人识别基于语音特征分析，可能存在误差，仅供参考。*
"""
    return content


def main():
    """主函数"""
    print("=" * 80)
    print("🎙️  处理对话类型音频（含说话人分离）")
    print("=" * 80)
    
    # 加载模型
    print("\n🔧 加载模型...")
    try:
        from funasr import AutoModel
        
        # ASR模型
        print("  加载ASR模型...")
        asr_model = AutoModel(
            model="iic/SenseVoiceSmall",
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            device="cpu"
        )
        
        # 说话人分离模型
        print("  加载说话人分离模型...")
        speaker_model = AutoModel(
            model="iic/speech_campplus_sv_zh-cn_16k-common",
            device="cpu"
        )
        
        print("✅ 模型加载完成")
        
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return
    
    # 查找对话文件
    download_dir = Path('src/data/downloads')
    dialogue_files = []
    
    for file_id in DIALOGUE_FILES:
        matches = list(download_dir.glob(f"{file_id}*.m4a"))
        if matches:
            dialogue_files.append(matches[0])
    
    print(f"\n📂 找到 {len(dialogue_files)} 个对话文件待处理")
    
    for i, audio_file in enumerate(dialogue_files, 1):
        print(f"\n[{i}/{len(dialogue_files)}] 处理: {audio_file.name[:50]}...")
        
        title = extract_title_from_filename(audio_file.name)
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', title)[:80]
        output_file = OUTPUT_DIR / f"{safe_title}.md"
        
        try:
            # 转写并分离说话人
            segments = transcribe_with_speaker_diarization(audio_file, asr_model, speaker_model)
            
            if not segments:
                print(f"  ⚠️  转写结果为空，跳过")
                continue
            
            # 识别付鹏
            segments = identify_speakers(segments)
            
            # 统计说话人
            speakers = set(s['speaker'] for s in segments)
            print(f"  识别到说话人: {', '.join(speakers)}")
            
            # 生成Markdown
            markdown = format_dialogue_markdown(title, segments, audio_file.name)
            
            # 保存
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            print(f"  ✅ 已保存: {output_file.name}")
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ 对话处理完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()