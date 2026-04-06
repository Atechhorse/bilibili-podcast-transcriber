"""
B站在线下载器 - 使用第三方API服务
"""
import requests
import time
from pathlib import Path
from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BilibiliOnlineDownloader:
    """使用在线API下载B站视频"""
    
    def __init__(self):
        self.download_dir = Path('data/downloads')
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # 多个备用API
        self.api_endpoints = [
            {
                'name': 'SaveFrom',
                'parse_url': 'https://api.savefrom.net/info',
                'method': 'get'
            },
            {
                'name': 'VideoFK',
                'parse_url': 'https://www.videofk.com/api/json/resolve',
                'method': 'get'
            }
        ]
    
    def download(self, bv_id: str, video_url: str) -> str:
        """
        下载B站视频
        
        Args:
            bv_id: BV号
            video_url: 视频URL
            
        Returns:
            下载的文件路径
        """
        logger.info(f"尝试使用在线服务下载: {video_url}")
        
        # 方法1: 尝试使用SaveFrom API
        try:
            return self._download_via_savefrom(bv_id, video_url)
        except Exception as e:
            logger.warning(f"SaveFrom 下载失败: {e}")
        
        # 方法2: 尝试直接解析B站视频流
        try:
            return self._download_via_bili_api(bv_id, video_url)
        except Exception as e:
            logger.warning(f"Bilibili API 下载失败: {e}")
        
        # 所有方法都失败
        raise Exception("所有下载方法都失败，B站可能需要登录才能访问此视频")
    
    def _download_via_savefrom(self, bv_id: str, video_url: str) -> str:
        """通过 SaveFrom.net API 下载"""
        api_url = f"https://api.savefrom.net/info?url={video_url}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析返回的数据
        data = response.json()
        
        if not data.get('url'):
            raise Exception("无法解析视频链接")
        
        # 下载视频
        video_download_url = data['url'][0]['url']
        return self._download_file(video_download_url, bv_id, data.get('meta', {}).get('title', 'video'))
    
    def _download_via_bili_api(self, bv_id: str, video_url: str) -> str:
        """
        尝试通过B站公开API下载（不需要登录的部分）
        注意：此方法可能只适用于部分公开视频
        """
        # 获取视频基本信息
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data['code'] != 0:
            raise Exception(f"B站API返回错误: {data.get('message', 'Unknown error')}")
        
        video_info = data['data']
        title = video_info['title']
        cid = video_info['cid']
        
        logger.info(f"视频标题: {title}")
        
        # 获取视频播放地址（需要登录才能获取高清）
        play_url_api = f"https://api.bilibili.com/x/player/playurl?bvid={bv_id}&cid={cid}&qn=64"
        
        response = requests.get(play_url_api, headers=headers, timeout=10)
        response.raise_for_status()
        
        play_data = response.json()
        
        if play_data['code'] != 0:
            raise Exception(f"无法获取播放地址: {play_data.get('message', 'Unknown error')}")
        
        # 获取视频URL
        video_url_data = play_data['data']['durl'][0]['url']
        
        return self._download_file(video_url_data, bv_id, title)
    
    def _download_file(self, url: str, bv_id: str, title: str) -> str:
        """下载文件"""
        # 清理文件名
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:100]  # 限制长度
        
        output_path = self.download_dir / f"{bv_id}_{safe_title}.mp4"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.bilibili.com/'
        }
        
        logger.info(f"开始下载: {output_path}")
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 每10MB打印一次进度
                    if downloaded % (10 * 1024 * 1024) == 0:
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(f"下载进度: {progress:.1f}%")
        
        logger.info(f"下载完成: {output_path}")
        return str(output_path)


def test_download():
    """测试下载功能"""
    downloader = BilibiliOnlineDownloader()
    
    # 测试一个公开视频
    test_url = "https://www.bilibili.com/video/BV14RrKBNEdH/"
    test_bv = "BV14RrKBNEdH"
    
    try:
        result = downloader.download(test_bv, test_url)
        print(f"✓ 下载成功: {result}")
    except Exception as e:
        print(f"✗ 下载失败: {e}")


if __name__ == '__main__':
    test_download()