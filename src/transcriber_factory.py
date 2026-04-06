"""
转写器工厂模块
根据配置选择使用 FunASR 或 Whisper
"""
from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


def create_transcriber(config: Dict):
    """
    根据配置创建转写器实例
    
    Args:
        config: 配置字典
        
    Returns:
        转写器实例（FunASRTranscriber 或 Transcriber）
    """
    asr_engine = config.get('asr_engine', 'funasr').lower()
    
    if asr_engine == 'funasr':
        logger.info("使用 FunASR 引擎（推荐用于中文）")
        try:
            from src.funasr_transcriber import FunASRTranscriber
            return FunASRTranscriber(config)
        except ImportError as e:
            logger.error(f"FunASR 未安装: {e}")
            logger.error("请运行: pip install -U funasr modelscope")
            logger.warning("回退到 Whisper 引擎")
            from src.transcriber import Transcriber
            return Transcriber(config)
    
    elif asr_engine == 'whisper':
        logger.info("使用 Whisper 引擎")
        from src.transcriber import Transcriber
        return Transcriber(config)
    
    else:
        logger.error(f"未知的 ASR 引擎: {asr_engine}")
        logger.info("使用默认引擎: FunASR")
        from src.funasr_transcriber import FunASRTranscriber
        return FunASRTranscriber(config)