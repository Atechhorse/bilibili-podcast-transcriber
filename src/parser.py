"""
链接解析模块
"""
import re
from typing import List, Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class LinkParser:
    """链接解析器"""
    
    # Bilibili 链接正则
    BILIBILI_PATTERN = re.compile(
        r'(?:https?://)?(?:www\.)?bilibili\.com/video/(BV[a-zA-Z0-9]+)',
        re.IGNORECASE
    )
    
    # 小宇宙链接正则
    XIAOYUZHOU_PATTERN = re.compile(
        r'(?:https?://)?(?:www\.)?xiaoyuzhoufm\.com/episode/([a-f0-9]+)',
        re.IGNORECASE
    )
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """
        解析链接文件
        
        Args:
            file_path: 链接文件路径
            
        Returns:
            链接对象列表，每个对象包含 url, platform, id 字段
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            return []
        
        links = []
        seen_urls = set()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 解析链接
            link_obj = self._parse_line(line)
            
            if link_obj:
                # 去重
                normalized_url = link_obj['url']
                if normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    links.append(link_obj)
                    logger.debug(f"第 {line_num} 行: {link_obj['platform']} - {link_obj['id']}")
                else:
                    logger.debug(f"第 {line_num} 行: 重复链接，已跳过")
            else:
                logger.warning(f"第 {line_num} 行: 无法识别的链接格式: {line}")
        
        return links
    
    def _parse_line(self, line: str) -> Dict:
        """
        解析单行链接
        
        Returns:
            包含 url, platform, id 的字典，失败返回 None
        """
        # 尝试匹配 Bilibili
        match = self.BILIBILI_PATTERN.search(line)
        if match:
            bv_id = match.group(1)
            normalized_url = f"https://www.bilibili.com/video/{bv_id}/"
            return {
                'url': normalized_url,
                'platform': 'bilibili',
                'id': bv_id,
                'original_url': line
            }
        
        # 尝试匹配小宇宙
        match = self.XIAOYUZHOU_PATTERN.search(line)
        if match:
            episode_id = match.group(1)
            normalized_url = f"https://www.xiaoyuzhoufm.com/episode/{episode_id}"
            return {
                'url': normalized_url,
                'platform': 'xiaoyuzhou',
                'id': episode_id,
                'original_url': line
            }
        
        return None