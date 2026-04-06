"""
音频下载模块
"""
import os
from pathlib import Path
from typing import Dict
import yt_dlp
import requests
from bs4 import BeautifulSoup
from utils.logger import setup_logger

logger = setup_logger(__name__)

# 尝试导入在线下载器
try:
    from bilibili_online_downloader import BilibiliOnlineDownloader
    ONLINE_DOWNLOADER_AVAILABLE = True
except ImportError:
    ONLINE_DOWNLOADER_AVAILABLE = False
    logger.warning("在线下载器不可用")


class Downloader:
    """音频下载器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.download_dir = Path('data/downloads')
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = config.get('processing', {}).get('max_retries', 3)
        
        # 初始化在线下载器（备用方案）
        if ONLINE_DOWNLOADER_AVAILABLE:
            self.online_downloader = BilibiliOnlineDownloader()
            logger.info("在线下载器已启用")
    
    def download(self, link: Dict) -> str:
        """
        下载音频
        
        Args:
            link: 链接对象
            
        Returns:
            下载的音频文件路径
        """
        platform = link['platform']
        
        for attempt in range(self.max_retries):
            try:
                if platform == 'bilibili':
                    return self._download_bilibili(link)
                elif platform == 'xiaoyuzhou':
                    return self._download_xiaoyuzhou(link)
                else:
                    raise ValueError(f"不支持的平台: {platform}")
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"下载失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                else:
                    # 最后一次尝试：如果是B站且有在线下载器，尝试使用它
                    if platform == 'bilibili' and ONLINE_DOWNLOADER_AVAILABLE:
                        logger.info("尝试使用在线下载器作为备用方案...")
                        try:
                            return self.online_downloader.download(link['id'], link['url'])
                        except Exception as online_error:
                            logger.error(f"在线下载器也失败了: {online_error}")
                    raise
    
    def _download_bilibili(self, link: Dict) -> str:
        """使用 yt-dlp 下载 Bilibili 音频"""
        url = link['url']
        bv_id = link['id']
        
        output_template = str(self.download_dir / f'{bv_id}_%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # 添加 User-Agent 和 Referer
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Referer': 'https://www.bilibili.com/'
            },
        }
        
        # 如果存在 cookies 文件，使用它
        cookies_file = Path('cookies.txt')
        if cookies_file.exists():
            ydl_opts['cookiefile'] = str(cookies_file)
            logger.info(f"使用 cookies 文件: {cookies_file}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # 获取实际下载的文件名
            filename = ydl.prepare_filename(info)
            # 替换扩展名为 mp3
            audio_path = Path(filename).with_suffix('.mp3')
            
            if not audio_path.exists():
                raise FileNotFoundError(f"下载的文件不存在: {audio_path}")
            
            return str(audio_path)
    
    def _download_xiaoyuzhou(self, link: Dict) -> str:
        """下载小宇宙音频"""
        url = link['url']
        episode_id = link['id']
        
        # 首先尝试使用 yt-dlp
        try:
            return self._download_xiaoyuzhou_ytdlp(link)
        except Exception as e:
            logger.warning(f"yt-dlp 下载失败，尝试直接抓取: {e}")
            return self._download_xiaoyuzhou_direct(link)
    
    def _download_xiaoyuzhou_ytdlp(self, link: Dict) -> str:
        """使用 yt-dlp 下载小宇宙"""
        url = link['url']
        episode_id = link['id']
        
        output_template = str(self.download_dir / f'xiaoyuzhou_{episode_id}_%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'quiet': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not Path(filename).exists():
                raise FileNotFoundError(f"下载的文件不存在: {filename}")
            
            return filename
    
    def _download_xiaoyuzhou_direct(self, link: Dict) -> str:
        """直接抓取小宇宙音频链接"""
        url = link['url']
        episode_id = link['id']
        
        # 请求页面获取音频链接
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找音频链接
        audio_url = None
        
        # 方法1: 查找 audio 标签
        audio_tag = soup.find('audio')
        if audio_tag and audio_tag.get('src'):
            audio_url = audio_tag['src']
        
        # 方法2: 查找 meta 标签
        if not audio_url:
            meta_tag = soup.find('meta', property='og:audio')
            if meta_tag:
                audio_url = meta_tag.get('content')
        
        if not audio_url:
            raise ValueError("无法找到音频链接")
        
        # 下载音频
        logger.info(f"找到音频链接: {audio_url}")
        audio_response = requests.get(audio_url, headers=headers, stream=True)
        audio_response.raise_for_status()
        
        # 保存文件
        output_path = self.download_dir / f'xiaoyuzhou_{episode_id}.mp3'
        
        with open(output_path, 'wb') as f:
            for chunk in audio_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"音频已保存: {output_path}")
        return str(output_path)