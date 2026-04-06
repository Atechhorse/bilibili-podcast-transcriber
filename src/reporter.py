"""
报告生成模块
"""
from pathlib import Path
from typing import List, Dict
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Reporter:
    """报告生成器"""
    
    def __init__(self):
        self.transcript_dir = Path('data/transcripts')
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_metadata_table(self, metadata_list: List[Dict], output_path: str):
        """
        生成元数据汇总表格（需求4）
        
        Args:
            metadata_list: 元数据列表
            output_path: 输出 Excel 文件路径
        """
        if not metadata_list:
            logger.warning("元数据列表为空，跳过表格生成")
            return
        
        # 构建 DataFrame
        df = pd.DataFrame(metadata_list)
        
        # 重新排列列顺序
        columns_order = [
            'platform', 'id', 'title', 'author', 
            'upload_date', 'duration', 'view_count',
            'original_url', 'normalized_url'
        ]
        
        # 只保留存在的列
        columns = [col for col in columns_order if col in df.columns]
        df = df[columns]
        
        # 添加序号
        df.insert(0, '序号', range(1, len(df) + 1))
        
        # 保存为 Excel
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        logger.info(f"元数据表格已生成: {output_path} (共 {len(df)} 条记录)")
    
    def generate_transcript(
        self, transcript: List[Dict], metadata: Dict, link: Dict
    ) -> str:
        """
        生成逐字稿 Markdown 文件
        
        Args:
            transcript: 转写结果列表
            metadata: 元数据
            link: 链接对象
            
        Returns:
            输出文件路径
        """
        platform = link['platform']
        link_id = link['id']
        
        # 构建文件名
        title = metadata.get('title', 'unknown').replace('/', '_')
        filename = f"{platform}_{link_id}_{title[:50]}.md"
        output_path = self.transcript_dir / filename
        
        # 生成 Markdown 内容
        content = []
        content.append(f"# {metadata.get('title', '未知标题')}\n")
        content.append("## 信息\n")
        content.append(f"- 平台: {metadata.get('platform', 'N/A')}")
        content.append(f"- 作者/播客: {metadata.get('author', 'N/A')}")
        content.append(f"- 时长: {metadata.get('duration', 'N/A')}")
        content.append(f"- 发布时间: {metadata.get('upload_date', 'N/A')}")
        content.append(f"- 链接: {link['url']}\n")
        
        content.append("## 逐字稿\n")
        
        current_speaker = None
        for item in transcript:
            speaker = item.get('speaker', '付鹏')
            text = item.get('text', '')
            start_time = self._format_time(item.get('start', 0))
            emotion = item.get('emotion', '')
            
            # 说话人变化时添加标题
            if speaker != current_speaker:
                emotion_tag = f" [{emotion}]" if emotion and emotion != 'NEUTRAL' else ""
                content.append(f"\n**[{start_time}] {speaker}{emotion_tag}**:\n")
                current_speaker = speaker
            
            content.append(text)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        logger.info(f"逐字稿已生成: {output_path}")
        return str(output_path)
    
    def generate_summary_report(self, progress_manager, output_path: str):
        """
        生成处理结果汇总表格
        
        Args:
            progress_manager: 进度管理器
            output_path: 输出 Excel 文件路径
        """
        progress_data = progress_manager.data
        
        if not progress_data:
            logger.warning("没有处理记录，跳过汇总报告生成")
            return
        
        # 构建记录列表
        records = []
        for url, info in progress_data.items():
            metadata = info.get('metadata', {})
            records.append({
                '序号': len(records) + 1,
                '平台': metadata.get('platform', 'N/A'),
                'ID': metadata.get('id', 'N/A'),
                '标题': metadata.get('title', 'N/A'),
                '作者': metadata.get('author', 'N/A'),
                '时长': metadata.get('duration', 'N/A'),
                '下载状态': '成功' if info.get('audio_path') else '失败',
                '转写状态': '成功' if info.get('transcript') else '失败',
                '处理状态': info.get('status', 'unknown'),
                '逐字稿路径': info.get('transcript_path', 'N/A'),
                '错误信息': info.get('error', ''),
                '原始链接': url,
            })
        
        df = pd.DataFrame(records)
        
        # 保存为 Excel
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False, engine='openpyxl')
        
        logger.info(f"处理结果汇总已生成: {output_path}")
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """格式化时间戳"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"