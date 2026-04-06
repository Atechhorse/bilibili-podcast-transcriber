"""
链接元数据提取模块
"""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict
import yt_dlp
from utils.logger import setup_logger

logger = setup_logger(__name__)


class MetadataExtractor:
    """元数据提取器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def extract(self, link: Dict) -> Dict:
        """
        提取链接元数据
        
        Args:
            link: 链接对象，包含 url, platform, id
            
        Returns:
            元数据字典
        """
        platform = link['platform']
        
        if platform == 'bilibili':
            return self._extract_bilibili(link)
        elif platform == 'xiaoyuzhou':
            return self._extract_xiaoyuzhou(link)
        else:
            raise ValueError(f"不支持的平台: {platform}")
    
    def _extract_bilibili(self, link: Dict) -> Dict:
        """提取 Bilibili 视频元数据"""
        url = link['url']
        bv_id = link['id']
        
        try:
            # 使用 yt-dlp 提取元数据
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                metadata = {
                    'platform': 'Bilibili',
                    'id': bv_id,
                    'title': info.get('title', 'N/A'),
                    'author': info.get('uploader', 'N/A'),
                    'upload_date': info.get('upload_date', 'N/A'),
                    'duration': self._format_duration(info.get('duration', 0)),
                    'view_count': info.get('view_count', 0),
                    'original_url': link['original_url'],
                    'normalized_url': url,
                }
                
                logger.debug(f"Bilibili 元数据: {metadata['title']}")
                return metadata
                
        except Exception as e:
            logger.error(f"Bilibili 元数据提取失败: {e}")
            # 返回基本信息
            return {
                'platform': 'Bilibili',
                'id': bv_id,
                'title': 'N/A',
                'author': 'N/A',
                'upload_date': 'N/A',
                'duration': 'N/A',
                'view_count': 0,
                'original_url': link['original_url'],
                'normalized_url': url,
                'error': str(e)
            }
    
    def _extract_xiaoyuzhou(self, link: Dict) -> Dict:
        """提取小宇宙播客元数据"""
        url = link['url']
        episode_id = link['id']
        
        try:
            # 请求页面
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title_tag = soup.find('meta', property='og:title')
            title = title_tag['content'] if title_tag else 'N/A'
            
            # 提取描述（可能包含播客名）
            desc_tag = soup.find('meta', property='og:description')
            description = desc_tag['content'] if desc_tag else ''
            
            # 提取播客名（通常在页面中）
            podcast_name = 'N/A'
            podcast_tag = soup.find('a', class_=re.compile('podcast'))
            if podcast_tag:
                podcast_name = podcast_tag.get_text(strip=True)
            
            # 提取时长（从页面脚本或标签中）
            duration = 'N/A'
            duration_tag = soup.find('span', class_=re.compile('duration'))
            if duration_tag:
                duration = duration_tag.get_text(strip=True)
            
            metadata = {
                'platform': '小宇宙',
                'id': episode_id,
                'title': title,
                'author': podcast_name,
                'upload_date': 'N/A',
                'duration': duration,
                'view_count': 0,
                'original_url': link['original_url'],
                'normalized_url': url,
            }
            
            logger.debug(f"小宇宙元数据: {metadata['title']}")
            return metadata
            
        except Exception as e:
            logger.error(f"小宇宙元数据提取失败: {e}")
            return {
                'platform': '小宇宙',
                'id': episode_id,
                'title': 'N/A',
                'author': 'N/A',
                'upload_date': 'N/A',
                'duration': 'N/A',
                'view_count': 0,
                'original_url': link['original_url'],
                'normalized_url': url,
                'error': str(e)
            }
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """格式化时长"""
        if seconds == 0:
            return 'N/A'
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"