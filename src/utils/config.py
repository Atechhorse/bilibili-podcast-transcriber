"""
配置管理
"""
import yaml
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)


def load_config(config_path: str) -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
        return get_default_config()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"配置文件加载成功: {config_path}")
        return config
    except Exception as e:
        logger.error(f"配置文件加载失败: {e}，使用默认配置")
        return get_default_config()


def get_default_config() -> dict:
    """获取默认配置"""
    return {
        'huggingface_token': None,
        'llm': {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'api_key': None,
            'base_url': 'https://api.deepseek.com'
        },
        'whisper': {
            'model_size': 'medium',
            'device': 'auto'
        },
        'processing': {
            'max_retries': 3,
            'segment_duration_minutes': 10,
            'segment_threshold_minutes': 30
        }
    }