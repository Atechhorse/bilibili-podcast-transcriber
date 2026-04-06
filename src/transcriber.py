"""
音频处理与转写模块
"""
import os
import json
from pathlib import Path
from typing import Dict, List
import whisper
from pyannote.audio import Pipeline
import torch
import ffmpeg
from utils.logger import setup_logger
from utils.llm_client import LLMClient

logger = setup_logger(__name__)


class Transcriber:
    """语音转写与说话人识别"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.temp_dir = Path('data/temp')
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载 Whisper 模型
        whisper_config = config.get('whisper', {})
        model_size = whisper_config.get('model_size', 'medium')
        device = whisper_config.get('device', 'auto')
        
        if device == 'auto':
            if torch.cuda.is_available():
                device = 'cuda'
            elif torch.backends.mps.is_available():
                device = 'mps'
            else:
                device = 'cpu'
        
        logger.info(f"加载 Whisper 模型: {model_size} (设备: {device})")
        self.whisper_model = whisper.load_model(model_size, device=device)
        self.device = device
        
        # 加载 Pyannote 说话人分离模型
        hf_token = config.get('huggingface_token')
        if hf_token:
            logger.info("加载 Pyannote 说话人分离模型")
            self.diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
            if device != 'cpu':
                self.diarization_pipeline.to(torch.device(device))
        else:
            logger.warning("未配置 HuggingFace token，将跳过说话人分离")
            self.diarization_pipeline = None
        
        # 初始化 LLM 客户端（用于说话人身份推理）
        self.llm_client = LLMClient(config.get('llm', {}))
        
        # 处理参数
        self.segment_threshold = config.get('processing', {}).get('segment_threshold_minutes', 30)
        self.segment_duration = config.get('processing', {}).get('segment_duration_minutes', 10)
    
    def transcribe(self, audio_path: str, platform: str = None) -> List[Dict]:
        """
        转写音频并识别说话人
        
        Args:
            audio_path: 音频文件路径
            platform: 平台类型（用于判断是否需要说话人分离）
            
        Returns:
            转写结果列表，每个元素包含 start, end, speaker, text
        """
        audio_path = Path(audio_path)
        
        # 预处理音频
        processed_audio = self._preprocess_audio(audio_path)
        
        # 检查是否需要分段
        duration = self._get_duration(processed_audio)
        logger.info(f"音频时长: {duration / 60:.1f} 分钟")
        
        if duration > self.segment_threshold * 60:
            logger.info(f"音频超过 {self.segment_threshold} 分钟，启用分段处理")
            return self._transcribe_segmented(processed_audio, platform)
        else:
            return self._transcribe_single(processed_audio, platform)
    
    def _preprocess_audio(self, audio_path: Path) -> Path:
        """预处理音频：转换为 16kHz WAV"""
        output_path = self.temp_dir / f"{audio_path.stem}_processed.wav"
        
        if output_path.exists():
            logger.debug(f"使用已存在的预处理音频: {output_path}")
            return output_path
        
        logger.info("预处理音频：转换为 16kHz WAV")
        try:
            (
                ffmpeg
                .input(str(audio_path))
                .output(str(output_path), ar=16000, ac=1, format='wav')
                .overwrite_output()
                .run(quiet=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"音频预处理失败: {e.stderr.decode()}")
            raise
        
        return output_path
    
    def _get_duration(self, audio_path: Path) -> float:
        """获取音频时长（秒）"""
        try:
            probe = ffmpeg.probe(str(audio_path))
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.warning(f"无法获取音频时长: {e}")
            return 0
    
    def _transcribe_single(self, audio_path: Path, platform: str) -> List[Dict]:
        """转写单个音频文件"""
        # 1. Whisper 转写
        logger.info("Whisper 转写中...")
        whisper_result = self.whisper_model.transcribe(
            str(audio_path),
            language='zh',
            verbose=False
        )
        
        # 2. 说话人分离
        if self.diarization_pipeline:
            logger.info("说话人分离中...")
            diarization = self.diarization_pipeline(str(audio_path))
        else:
            diarization = None
        
        # 3. 合并转写和说话人信息
        transcript = self._merge_transcription_and_diarization(
            whisper_result, diarization
        )
        
        # 4. 说话人身份识别
        if diarization:
            transcript = self._identify_speakers(transcript, platform)
        
        return transcript
    
    def _transcribe_segmented(self, audio_path: Path, platform: str) -> List[Dict]:
        """分段转写长音频"""
        duration = self._get_duration(audio_path)
        segment_length = self.segment_duration * 60
        num_segments = int(duration / segment_length) + 1
        
        logger.info(f"将音频分为 {num_segments} 段处理")
        
        all_transcripts = []
        
        for i in range(num_segments):
            start_time = i * segment_length
            end_time = min((i + 1) * segment_length, duration)
            
            logger.info(f"处理分段 {i + 1}/{num_segments} ({start_time:.1f}s - {end_time:.1f}s)")
            
            # 切分音频
            segment_path = self.temp_dir / f"{audio_path.stem}_segment_{i}.wav"
            self._extract_segment(audio_path, segment_path, start_time, end_time)
            
            # 转写分段
            segment_transcript = self._transcribe_single(segment_path, platform)
            
            # 调整时间戳
            for item in segment_transcript:
                item['start'] += start_time
                item['end'] += start_time
            
            all_transcripts.extend(segment_transcript)
            
            # 清理临时文件
            segment_path.unlink()
        
        return all_transcripts
    
    def _extract_segment(self, audio_path: Path, output_path: Path, start: float, end: float):
        """提取音频片段"""
        try:
            (
                ffmpeg
                .input(str(audio_path), ss=start, t=end - start)
                .output(str(output_path), ar=16000, ac=1, format='wav')
                .overwrite_output()
                .run(quiet=True)
            )
        except ffmpeg.Error as e:
            logger.error(f"音频分段失败: {e.stderr.decode()}")
            raise
    
    def _merge_transcription_and_diarization(
        self, whisper_result: Dict, diarization
    ) -> List[Dict]:
        """合并 Whisper 转写和说话人分离结果"""
        segments = whisper_result['segments']
        
        if not diarization:
            # 没有说话人分离，所有文本标记为 "付鹏"
            return [
                {
                    'start': seg['start'],
                    'end': seg['end'],
                    'speaker': '付鹏',
                    'text': seg['text'].strip()
                }
                for seg in segments
            ]
        
        # 构建说话人时间轴
        speaker_timeline = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_timeline.append({
                'start': turn.start,
                'end': turn.end,
                'speaker': speaker
            })
        
        # 为每个转写片段分配说话人
        result = []
        for seg in segments:
            seg_start = seg['start']
            seg_end = seg['end']
            seg_mid = (seg_start + seg_end) / 2
            
            # 找到中点时刻的说话人
            speaker = 'UNKNOWN'
            for spk in speaker_timeline:
                if spk['start'] <= seg_mid <= spk['end']:
                    speaker = spk['speaker']
                    break
            
            result.append({
                'start': seg_start,
                'end': seg_end,
                'speaker': speaker,
                'text': seg['text'].strip()
            })
        
        return result
    
    def _identify_speakers(self, transcript: List[Dict], platform: str) -> List[Dict]:
        """识别说话人身份"""
        # 获取所有唯一的说话人
        speakers = list(set(item['speaker'] for item in transcript))
        
        # 单人场景：直接标记为付鹏
        if len(speakers) == 1:
            logger.info("检测到单人场景，标记为付鹏")
            for item in transcript:
                item['speaker'] = '付鹏'
            return transcript
        
        # 多人场景：使用 LLM 推理
        logger.info(f"检测到 {len(speakers)} 个说话人，使用 LLM 进行身份推理")
        
        # 提取前 5 分钟的文本用于分析
        sample_text = []
        for item in transcript:
            if item['start'] > 300:  # 5分钟
                break
            sample_text.append(f"[{item['speaker']}]: {item['text']}")
        
        sample_str = '\n'.join(sample_text[:50])  # 最多50条
        
        # 构建 LLM 提示
        prompt = f"""以下是一段播客或视频的前几分钟对话转写，其中包含多个说话人（标记为 SPEAKER_00, SPEAKER_01 等）。
请分析对话内容，识别出哪个 Speaker ID 对应"付鹏"。

判断依据可能包括：
1. 自我介绍："我是付鹏"
2. 主持人介绍："欢迎付鹏先生"
3. 对话中的称呼和角色

对话内容：
{sample_str}

请直接回答哪个 Speaker ID 是付鹏，只需要回答 ID，例如 "SPEAKER_01"。如果无法确定，请回答 "UNKNOWN"。
"""
        
        try:
            response = self.llm_client.chat(prompt)
            fupeng_speaker = response.strip()
            
            # 验证返回的 ID 是否在说话人列表中
            if fupeng_speaker in speakers:
                logger.info(f"识别到付鹏对应的 Speaker ID: {fupeng_speaker}")
                
                # 替换说话人标签
                for item in transcript:
                    if item['speaker'] == fupeng_speaker:
                        item['speaker'] = '付鹏'
                    else:
                        item['speaker'] = '其他'
            else:
                logger.warning(f"LLM 返回了无效的 Speaker ID: {fupeng_speaker}")
                # 保留原始标签
                
        except Exception as e:
            logger.error(f"LLM 身份推理失败: {e}")
            # 保留原始标签
        
        return transcript