"""
进度管理模块
"""
import json
from pathlib import Path
from typing import Dict, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ProgressManager:
    """进度管理器"""
    
    def __init__(self, progress_file: str = 'progress.json'):
        self.progress_file = Path(progress_file)
        self.data = self._load()
    
    def _load(self) -> Dict:
        """加载进度文件"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"加载进度文件: {len(data)} 条记录")
                return data
            except Exception as e:
                logger.error(f"加载进度文件失败: {e}")
                return {}
        return {}
    
    def _save(self):
        """保存进度文件"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存进度文件失败: {e}")
    
    def get_status(self, url: str) -> str:
        """获取链接的处理状态"""
        return self.data.get(url, {}).get('status', 'pending')
    
    def update_status(self, url: str, status: str, **kwargs):
        """
        更新链接的处理状态
        
        Args:
            url: 链接
            status: 状态 (pending, metadata_extracted, downloaded, transcribed, completed, failed)
            **kwargs: 其他信息 (metadata, audio_path, transcript, transcript_path, error)
        """
        if url not in self.data:
            self.data[url] = {}
        
        self.data[url]['status'] = status
        self.data[url].update(kwargs)
        
        self._save()
        logger.debug(f"进度已更新: {url} -> {status}")
    
    def get_metadata(self, url: str) -> Optional[Dict]:
        """获取链接的元数据"""
        return self.data.get(url, {}).get('metadata')
    
    def get_audio_path(self, url: str) -> Optional[str]:
        """获取链接的音频路径"""
        return self.data.get(url, {}).get('audio_path')
    
    def get_transcript(self, url: str) -> Optional[list]:
        """获取链接的转写结果"""
        return self.data.get(url, {}).get('transcript')
    
    def reset(self):
        """重置所有进度"""
        self.data = {}
        self._save()
        logger.info("进度已重置")