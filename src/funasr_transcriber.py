"""
FunASR 音频处理与转写模块
支持高精度中文识别和说话人分离
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import torch
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FunASRTranscriber:
    """基于FunASR的语音转写与说话人识别"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.temp_dir = Path('data/temp')
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取设备配置
        funasr_config = config.get('funasr', {})
        device = funasr_config.get('device', 'auto')
        
        if device == 'auto':
            if torch.cuda.is_available():
                device = 'cuda'
            elif torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        
        self.device = device
        logger.info(f"FunASR 使用设备: {device}")
        
        # 延迟加载模型（首次使用时加载）
        self.asr_model = None
        self.vad_model = None
        self.speaker_model = None
        
        # 配置参数
        self.enable_speaker_diarization = funasr_config.get('enable_speaker_diarization', True)
        self.enable_emotion = funasr_config.get('enable_emotion', True)
        self.enable_itn = funasr_config.get('enable_itn', True)
        self.max_single_segment_time = funasr_config.get('max_single_segment_time', 30000)  # ms
    
    def _load_models(self):
        """延迟加载FunASR模型"""
        if self.asr_model is not None:
            return
        
        logger.info("正在加载 FunASR 模型...")
        
        try:
            from funasr import AutoModel
            
            # 加载ASR模型（SenseVoice - 支持情感识别）
            logger.info("加载 SenseVoice ASR 模型...")
            self.asr_model = AutoModel(
                model="iic/SenseVoiceSmall",
                device=self.device
            )
            logger.info("✓ ASR模型加载完成")
            
            # 加载VAD模型（语音端点检测）
            logger.info("加载 VAD 模型...")
            self.vad_model = AutoModel(
                model="fsmn-vad",
                device=self.device
            )
            logger.info("✓ VAD模型加载完成")
            
            # 加载说话人分离模型（如果启用）
            if self.enable_speaker_diarization:
                logger.info("加载说话人分离模型...")
                self.speaker_model = AutoModel(
                    model="iic/speech_campplus_sv_zh-cn_16k-common",
                    device=self.device
                )
                logger.info("✓ 说话人分离模型加载完成")
            
            logger.info("所有模型加载完成！")
            
        except ImportError as e:
            logger.error(f"FunASR未安装: {e}")
            logger.error("请运行: pip install -U funasr modelscope")
            raise
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def transcribe(self, audio_path: str, platform: str = None) -> List[Dict]:
        """
        转写音频并识别说话人
        
        Args:
            audio_path: 音频文件路径
            platform: 平台类型（用于判断是否需要说话人分离）
            
        Returns:
            转写结果列表，每个元素包含 start, end, speaker, text, emotion
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        logger.info(f"开始转写音频: {audio_path.name}")
        
        # 确保模型已加载
        self._load_models()
        
        # 执行转写
        transcript = self._transcribe_with_funasr(audio_path)
        
        # 如果启用说话人分离且检测到多人
        if self.enable_speaker_diarization and self._has_multiple_speakers(transcript):
            logger.info("检测到多人对话，启用说话人分离...")
            transcript = self._add_speaker_labels(audio_path, transcript)
        else:
            # 单人场景，标记为付鹏
            for item in transcript:
                item['speaker'] = '付鹏'
        
        logger.info(f"转写完成，共 {len(transcript)} 个片段")
        return transcript
    
    def _transcribe_with_funasr(self, audio_path: Path) -> List[Dict]:
        """使用FunASR进行转写"""
        logger.info("执行 FunASR 转写...")
        
        try:
            # 先使用VAD进行语音分段
            vad_result = self.vad_model.generate(
                input=str(audio_path),
                max_single_segment_time=self.max_single_segment_time
            )
            
            # 提取语音片段
            segments = self._extract_vad_segments(vad_result)
            logger.info(f"VAD检测到 {len(segments)} 个语音片段")
            
            # 对每个片段进行ASR识别
            transcript = []
            for i, segment in enumerate(segments):
                start_time = segment['start']
                end_time = segment['end']
                
                # 使用FunASR识别
                asr_result = self.asr_model.generate(
                    input=str(audio_path),
                    language="zh",
                    use_itn=self.enable_itn,
                    batch_size_s=300
                )
                
                # 解析结果
                text, emotion = self._parse_funasr_result(asr_result)
                
                if text.strip():
                    transcript.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text.strip(),
                        'emotion': emotion if self.enable_emotion else 'NEUTRAL',
                        'speaker': 'UNKNOWN'  # 稍后填充
                    })
            
            return transcript
            
        except Exception as e:
            logger.error(f"FunASR转写失败: {e}")
            raise
    
    def _extract_vad_segments(self, vad_result) -> List[Dict]:
        """从VAD结果中提取语音片段"""
        segments = []
        
        if isinstance(vad_result, list) and len(vad_result) > 0:
            for item in vad_result:
                if isinstance(item, dict) and 'value' in item:
                    # 解析VAD时间戳
                    for seg in item['value']:
                        segments.append({
                            'start': seg[0] / 1000.0,  # 转换为秒
                            'end': seg[1] / 1000.0
                        })
        else:
            # 如果VAD失败，返回整个音频作为一个片段
            segments.append({'start': 0, 'end': float('inf')})
        
        return segments
    
    def _parse_funasr_result(self, result) -> tuple:
        """
        解析FunASR结果，提取文本和情感
        
        Returns:
            (text, emotion) 元组
        """
        text = ""
        emotion = "NEUTRAL"
        
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict) and 'text' in item:
                    text += item['text']
        elif isinstance(result, dict):
            text = result.get('text', str(result))
        else:
            text = str(result)
        
        # 清理FunASR特殊标签
        text = self._clean_funasr_tags(text)
        
        # 提取情感标签
        emotion_match = re.search(r'<\|([A-Z]+)\|>', text)
        if emotion_match:
            emotion = emotion_match.group(1)
        
        return text, emotion
    
    def _clean_funasr_tags(self, text: str) -> str:
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
    
    def _has_multiple_speakers(self, transcript: List[Dict]) -> bool:
        """判断是否存在多个说话人（基于音频特征分析）"""
        # 简单策略：如果音频片段之间有较长停顿，可能是多人对话
        if len(transcript) < 2:
            return False
        
        # 计算片段之间的停顿时间
        pauses = []
        for i in range(len(transcript) - 1):
            pause = transcript[i+1]['start'] - transcript[i]['end']
            pauses.append(pause)
        
        # 如果有超过3秒的停顿，可能是多人对话
        long_pauses = [p for p in pauses if p > 3.0]
        
        return len(long_pauses) > 3
    
    def _add_speaker_labels(self, audio_path: Path, transcript: List[Dict]) -> List[Dict]:
        """
        添加说话人标签（使用说话人分离模型）
        """
        if self.speaker_model is None:
            logger.warning("说话人分离模型未加载，跳过")
            for item in transcript:
                item['speaker'] = '付鹏'
            return transcript
        
        try:
            logger.info("执行说话人分离...")
            
            # 使用FunASR的说话人分离
            speaker_result = self.speaker_model.generate(
                input=str(audio_path),
                cache={}
            )
            
            # 解析说话人信息
            speaker_timeline = self._parse_speaker_result(speaker_result)
            
            # 为每个片段分配说话人
            for item in transcript:
                mid_time = (item['start'] + item['end']) / 2
                speaker = self._find_speaker_at_time(speaker_timeline, mid_time)
                item['speaker'] = speaker
            
            # 识别主要说话人（付鹏）
            transcript = self._identify_main_speaker(transcript)
            
            return transcript
            
        except Exception as e:
            logger.error(f"说话人分离失败: {e}")
            # 失败时标记所有为付鹏
            for item in transcript:
                item['speaker'] = '付鹏'
            return transcript
    
    def _parse_speaker_result(self, result) -> List[Dict]:
        """解析说话人分离结果"""
        timeline = []
        
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    timeline.append({
                        'start': item.get('start', 0),
                        'end': item.get('end', 0),
                        'speaker': item.get('speaker', 'SPEAKER_00')
                    })
        
        return timeline
    
    def _find_speaker_at_time(self, timeline: List[Dict], time: float) -> str:
        """找到指定时间点的说话人"""
        for item in timeline:
            if item['start'] <= time <= item['end']:
                return item['speaker']
        
        return 'SPEAKER_00'
    
    def _identify_main_speaker(self, transcript: List[Dict]) -> List[Dict]:
        """识别主要说话人（付鹏）"""
        # 统计每个说话人的发言时长
        speaker_time = {}
        for item in transcript:
            speaker = item['speaker']
            duration = item['end'] - item['start']
            speaker_time[speaker] = speaker_time.get(speaker, 0) + duration
        
        # 发言最多的标记为付鹏
        if speaker_time:
            main_speaker = max(speaker_time, key=speaker_time.get)
            
            for item in transcript:
                if item['speaker'] == main_speaker:
                    item['speaker'] = '付鹏'
                else:
                    item['speaker'] = '其他'
        
        return transcript
    
    def format_transcript(self, transcript: List[Dict], include_timestamps: bool = True) -> str:
        """
        格式化转写结果为可读文本
        
        Args:
            transcript: 转写结果列表
            include_timestamps: 是否包含时间戳
            
        Returns:
            格式化后的文本
        """
        lines = []
        current_speaker = None
        current_paragraph = []
        
        for item in transcript:
            speaker = item.get('speaker', '付鹏')
            text = item['text']
            
            # 如果说话人改变，输出前一段
            if speaker != current_speaker and current_paragraph:
                paragraph_text = ''.join(current_paragraph)
                if include_timestamps:
                    lines.append(f"\n**[{current_speaker}]**\n{paragraph_text}\n")
                else:
                    lines.append(f"\n{paragraph_text}\n")
                current_paragraph = []
            
            current_speaker = speaker
            
            if include_timestamps:
                start_time = self._format_time(item['start'])
                current_paragraph.append(f"[{start_time}] {text} ")
            else:
                current_paragraph.append(text)
        
        # 输出最后一段
        if current_paragraph:
            paragraph_text = ''.join(current_paragraph)
            if include_timestamps:
                lines.append(f"\n**[{current_speaker}]**\n{paragraph_text}\n")
            else:
                lines.append(f"\n{paragraph_text}\n")
        
        return '\n'.join(lines)
    
    def _format_time(self, seconds: float) -> str:
        """格式化时间为 HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"