#!/usr/bin/env python3
"""
简化版主程序 - 仅做元数据提取和音频下载
适用于未安装 Whisper 和 Pyannote 的情况
"""
import argparse
import sys
from pathlib import Path

from parser import LinkParser
from metadata_extractor import MetadataExtractor
from downloader import Downloader
from reporter import Reporter
from progress_manager import ProgressManager
from utils.config import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description='视频/播客音频提取工具（简化版）')
    parser.add_argument('--input', default='视频链接', help='输入链接文件路径')
    parser.add_argument('--force', action='store_true', help='强制重新处理所有链接')
    parser.add_argument('--retry-failed', action='store_true', help='仅重试失败的链接')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config('config.yaml')
    
    # 初始化模块
    progress_manager = ProgressManager('progress.json')
    link_parser = LinkParser()
    metadata_extractor = MetadataExtractor(config)
    downloader = Downloader(config)
    reporter = Reporter()
    
    logger.info("=" * 60)
    logger.info("开始处理视频/播客链接（简化版 - 仅元数据+下载）")
    logger.info("=" * 60)
    
    # 解析链接
    logger.info(f"正在解析链接文件: {args.input}")
    links = link_parser.parse_file(args.input)
    logger.info(f"共解析到 {len(links)} 个有效链接")
    
    # 加载进度
    if args.force:
        logger.info("强制模式：忽略之前的进度，重新处理所有链接")
        progress_manager.reset()
    elif args.retry_failed:
        logger.info("重试模式：仅处理失败的链接")
        links = [link for link in links if progress_manager.get_status(link['url']) == 'failed']
        logger.info(f"找到 {len(links)} 个失败的链接待重试")
    
    # 第一步：提取所有链接的元数据（需求4）
    logger.info("\n" + "=" * 60)
    logger.info("步骤 1/2: 提取链接元数据")
    logger.info("=" * 60)
    
    metadata_list = []
    for i, link in enumerate(links, 1):
        url = link['url']
        if not args.force and progress_manager.get_status(url) in ['completed', 'downloaded', 'metadata_extracted']:
            logger.info(f"[{i}/{len(links)}] 跳过已处理: {url}")
            metadata = progress_manager.get_metadata(url)
            if metadata:
                metadata_list.append(metadata)
            continue
        
        try:
            logger.info(f"[{i}/{len(links)}] 正在提取元数据: {url}")
            metadata = metadata_extractor.extract(link)
            metadata_list.append(metadata)
            progress_manager.update_status(url, 'metadata_extracted', metadata=metadata)
            logger.info(f"  ✓ 标题: {metadata.get('title', 'N/A')}")
        except Exception as e:
            logger.error(f"  ✗ 元数据提取失败: {e}")
            progress_manager.update_status(url, 'failed', error=str(e))
    
    # 生成元数据汇总表格
    reporter.generate_metadata_table(metadata_list, 'data/links_summary.xlsx')
    logger.info(f"\n✓ 元数据表格已生成: data/links_summary.xlsx")
    
    # 第二步：下载音频
    logger.info("\n" + "=" * 60)
    logger.info("步骤 2/2: 下载音频文件")
    logger.info("=" * 60)
    
    downloaded_count = 0
    failed_count = 0
    
    for i, link in enumerate(links, 1):
        url = link['url']
        if not args.force and progress_manager.get_status(url) in ['completed', 'downloaded']:
            logger.info(f"[{i}/{len(links)}] 跳过已下载: {url}")
            downloaded_count += 1
            continue
        
        try:
            logger.info(f"[{i}/{len(links)}] 正在下载音频: {url}")
            audio_path = downloader.download(link)
            progress_manager.update_status(url, 'downloaded', audio_path=audio_path)
            logger.info(f"  ✓ 已保存: {audio_path}")
            downloaded_count += 1
        except Exception as e:
            logger.error(f"  ✗ 下载失败: {e}")
            progress_manager.update_status(url, 'failed', error=str(e))
            failed_count += 1
    
    logger.info("\n" + "=" * 60)
    logger.info("处理完成！")
    logger.info("=" * 60)
    logger.info(f"✓ 成功: {downloaded_count} 个")
    logger.info(f"✗ 失败: {failed_count} 个")
    logger.info(f"\n输出文件:")
    logger.info(f"  - 元数据表格: data/links_summary.xlsx")
    logger.info(f"  - 音频文件: data/downloads/")
    logger.info(f"  - 日志文件: logs/app.log")
    
    if failed_count > 0:
        logger.info(f"\n提示: 有 {failed_count} 个链接下载失败")
        logger.info("  可以运行: python main_simple.py --retry-failed")


if __name__ == '__main__':
    main()