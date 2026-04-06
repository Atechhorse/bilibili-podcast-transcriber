#!/usr/bin/env python3
"""
处理对话类型的音频文件 - 简化版
使用文本特征来区分说话人（不使用重型模型）
"""
import os
import sys
import re
import time
from pathlib import Path

# 对话类型的文件
DIALOGUE_FILES = {
    "vol.54 对话付鹏：当社会风险偏好变了，钱将流向何处？": "vol.54",
    "E146 对话付鹏：普通人如何有效捕捉属于自己的机会": "E146",
    "03 躺平or躺赚？未来三五年最确定的交易机会｜对话付鹏": "03 躺平",
    '12 "老登"经济学：不博、不熟、不被忽悠｜对话付鹏': "老登",
    "E136.听付鹏讲几个故事：关于逆潮、交易和玩儿": "E136",
    "付鹏：考古专业比计算机更有赚头！文科生的好日子还在后头？": "考古专业",
    "（01）揭秘谣言经济学：实名的人背锅，匿名的人发财？": "谣言经济学",
}

OUTPUT_DIR = Path('data/transcripts')


def clean_funasr_tags(text: str) -> str:
    """清理FunASR输出中的特殊标签"""
    text = re.sub(r'<\|[A-Za-z_]+\|>', '', text)
    return text.strip()


def analyze_dialogue_structure(text: str) -> list:
    """
    分析文本的对话结构，基于以下特征识别说话人：
    1. 问答模式：问号后通常换人
    2. 主持人特征：开场白、引导语、总结语
    3. 付鹏特征：专业术语、深度分析、个人观点
    """
    segments = []
    
    # 按句子分割
    # 使用更精确的分割方式
    sentences = []
    current = ""
    for char in text:
        current += char
        if char in '。！？':
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())
    
    # 主持人特征词
    host_patterns = [
        r'^(那么?|所以说?|你觉得|你怎么看|你认为|关于这个|我们来聊聊|接下来|好的|对|是的|嗯)',
        r'^(首先|其次|最后|另外|还有一个问题|还想问)',
        r'(是这样吗|对吗|是吧|对不对|怎么样|如何|什么时候)',
        r'^欢迎.*来到',
        r'^今天.*请到',
        r'^感谢.*收听',
    ]
    
    # 付鹏特征词（专业分析）
    fupeng_patterns = [
        r'(其实|本质上|逻辑是|核心是|简单说|我跟你讲|我告诉你)',
        r'(投资|资产|配置|周期|通胀|通缩|杠杆|负债|风险|收益)',
        r'(市场|经济|金融|股票|债券|房产|利率|货币|GDP)',
        r'(我认为|我觉得|我一直说|我经常讲|我之前说过)',
        r'(举个例子|比如说|打个比方)',
    ]
    
    current_speaker = '主持人'  # 假设开始是主持人
    current_text = []
    last_was_question = False
    question_count = 0
    
    for sentence in sentences:
        if not sentence:
            continue
        
        # 检测是否是主持人
        is_host_style = False
        for pattern in host_patterns:
            if re.search(pattern, sentence):
                is_host_style = True
                break
        
        # 检测是否是付鹏风格
        is_fupeng_style = False
        fupeng_score = 0
        for pattern in fupeng_patterns:
            if re.search(pattern, sentence):
                fupeng_score += 1
        if fupeng_score >= 2:
            is_fupeng_style = True
        
        # 判断是否需要切换说话人
        switch = False
        new_speaker = current_speaker
        
        # 规则1：问号后面如果是专业分析，切换到付鹏
        if last_was_question and is_fupeng_style:
            if current_speaker == '主持人':
                switch = True
                new_speaker = '付鹏'
        
        # 规则2：长段专业分析后出现问句，可能是主持人
        if is_host_style and current_speaker == '付鹏' and len(''.join(current_text)) > 300:
            switch = True
            new_speaker = '主持人'
        
        # 规则3：明显的主持人开场/引导语
        if re.match(r'^(那么?|好的|是的|对|嗯).{0,10}(呢|吗|吧)[？?]?$', sentence):
            if current_speaker == '付鹏':
                switch = True
                new_speaker = '主持人'
        
        # 执行切换
        if switch and current_text:
            segments.append({
                'speaker': current_speaker,
                'text': ''.join(current_text)
            })
            current_text = []
            current_speaker = new_speaker
        
        current_text.append(sentence)
        last_was_question = sentence.endswith('？') or sentence.endswith('?')
        if last_was_question:
            question_count += 1
    
    # 保存最后一段
    if current_text:
        segments.append({
            'speaker': current_speaker,
            'text': ''.join(current_text)
        })
    
    return segments


def optimize_segments(segments: list) -> list:
    """
    优化分段：
    1. 合并过短的相邻同speaker段落
    2. 根据发言量重新识别付鹏（发言最多的是付鹏）
    """
    if not segments:
        return segments
    
    # 合并过短的相邻段落
    merged = []
    for seg in segments:
        if merged and merged[-1]['speaker'] == seg['speaker']:
            merged[-1]['text'] += seg['text']
        elif merged and len(seg['text']) < 50:
            # 过短的段落合并到上一个
            merged[-1]['text'] += seg['text']
        else:
            merged.append(dict(seg))
    
    # 统计发言量
    speaker_len = {}
    for seg in merged:
        speaker = seg['speaker']
        speaker_len[speaker] = speaker_len.get(speaker, 0) + len(seg['text'])
    
    # 发言最多的是付鹏
    if speaker_len:
        max_speaker = max(speaker_len, key=speaker_len.get)
        
        # 如果主持人说得比付鹏多，需要交换
        if max_speaker == '主持人':
            for seg in merged:
                if seg['speaker'] == '主持人':
                    seg['speaker'] = '付鹏'
                elif seg['speaker'] == '付鹏':
                    seg['speaker'] = '主持人'
    
    return merged


def format_dialogue_markdown(title: str, segments: list, source_file: str = "") -> str:
    """格式化为对话式Markdown"""
    content = f"""# {title}

## 基本信息

- **来源平台**: 小宇宙
- **类型**: 对话/访谈
- **转写引擎**: FunASR SenseVoice
- **生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

## 对话内容

"""
    
    for seg in segments:
        speaker = seg['speaker']
        text = seg['text']
        
        # 分行处理长文本
        if len(text) > 150:
            # 按句子分段显示
            formatted_lines = []
            current_line = ""
            for char in text:
                current_line += char
                if char in '。！？' and len(current_line) > 50:
                    formatted_lines.append(current_line)
                    current_line = ""
            if current_line:
                formatted_lines.append(current_line)
            
            text = '\n'.join(formatted_lines)
        
        content += f"**{speaker}**：{text}\n\n"
    
    content += """---

*本文档由AI自动转写生成，说话人识别基于文本特征分析，可能存在误差。*
"""
    return content


def process_existing_transcripts():
    """处理已存在的转写文档，转换为对话格式"""
    print("=" * 80)
    print("??️  处理对话类型文档（基于文本分析）")
    print("=" * 80)
    
    processed = 0
    
    for title_key, file_prefix in DIALOGUE_FILES.items():
        # 查找对应的md文件
        md_files = list(OUTPUT_DIR.glob(f"*{file_prefix}*.md"))
        
        if not md_files:
            print(f"\n⚠️  未找到: {title_key[:40]}...")
            continue
        
        md_file = md_files[0]
        print(f"\n[{processed+1}/{len(DIALOGUE_FILES)}] 处理: {md_file.name[:50]}...")
        
        try:
            # 读取现有内容
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取正文内容（跳过头部元信息）
            if '## 内容' in content:
                text_start = content.find('## 内容')
                text_end = content.find('---', text_start + 10)
                if text_end == -1:
                    text_end = content.find('*本文档由AI', text_start)
                
                main_text = content[text_start+7:text_end].strip()
            elif '## 对话内容' in content:
                # 已经是对话格式，跳过
                print(f"  ⏭️  已是对话格式，跳过")
                continue
            else:
                # 直接使用全部内容
                main_text = content
            
            # 清理标签
            main_text = clean_funasr_tags(main_text)
            
            # 分析对话结构
            segments = analyze_dialogue_structure(main_text)
            
            # 优化分段
            segments = optimize_segments(segments)
            
            # 统计说话人
            speakers = {}
            for seg in segments:
                sp = seg['speaker']
                speakers[sp] = speakers.get(sp, 0) + 1
            
            print(f"  识别到说话人: {', '.join([f'{k}({v}段)' for k,v in speakers.items()])}")
            
            # 生成新的Markdown
            title = md_file.stem
            new_content = format_dialogue_markdown(title, segments)
            
            # 保存
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✅ 已更新: {md_file.name}")
            processed += 1
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print(f"✅ 完成！已处理 {processed} 个对话文档")
    print("=" * 80)


if __name__ == '__main__':
    process_existing_transcripts()