#!/usr/bin/env python3
"""
视频/播客音频提取与逐字稿生成项目主程序
"""
import argparse
import sys
from pathlib import Path

from parser import LinkParser
from metadata_extractor import MetadataExtractor
from downloader import Downloader
from transcriber_factory import create_transcriber
from reporter import Reporter
from progress_manager import ProgressManager
from utils.config import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser(description='视频/播客音频提取与逐字稿生成工具')
    parser.add_argument('--input', default='视频链接', help='输入链接文件路径')
    parser.add_argument('--force', action='store_true', help='强制重新处理所有链接')
    parser.add_argument('--retry-failed', action='store_true', help='仅重试失败的链接')
    parser.add_argument('--resume', action='store_true', default=True, help='从上次中断处继续（默认）')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config('config.yaml')
    
    # 初始化模块
    progress_manager = ProgressManager('progress.json')
    link_parser = LinkParser()
    metadata_extractor = MetadataExtractor(config)
    downloader = Downloader(config)
    transcriber = create_transcriber(config)  # 使用工厂创建转写器
    reporter = Reporter()
    
    logger.info("=" * 60)
    logger.info("开始处理视频/播客链接")
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
    else:
        logger.info("续传模式：跳过已完成的链接")
    
    # 第一步：提取所有链接的元数据（需求4）
    logger.info("\n" + "=" * 60)
    logger.info("步骤 1/4: 提取链接元数据")
    logger.info("=" * 60)
    
    metadata_list = []
    for i, link in enumerate(links, 1):
        url = link['url']
        if not args.force and progress_manager.get_status(url) in ['completed', 'metadata_extracted']:
            logger.info(f"[{i}/{len(links)}] 跳过已处理: {url}")
            metadata_list.append(progress_manager.get_metadata(url))
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
    logger.info("步骤 2/4: 下载音频文件")
    logger.info("=" * 60)
    
    downloaded_files = []
    for i, link in enumerate(links, 1):
        url = link['url']
        if not args.force and progress_manager.get_status(url) in ['completed', 'downloaded', 'transcribed']:
            logger.info(f"[{i}/{len(links)}] 跳过已下载: {url}")
            downloaded_files.append(progress_manager.get_audio_path(url))
            continue
        
        try:
            logger.info(f"[{i}/{len(links)}] 正在下载音频: {url}")
            audio_path = downloader.download(link)
            downloaded_files.append(audio_path)
            progress_manager.update_status(url, 'downloaded', audio_path=audio_path)
            logger.info(f"  ✓ 已保存: {audio_path}")
        except Exception as e:
            logger.error(f"  ✗ 下载失败: {e}")
            progress_manager.update_status(url, 'failed', error=str(e))
            downloaded_files.append(None)
    
    # 第三步：转写与说话人识别
    logger.info("\n" + "=" * 60)
    logger.info("步骤 3/4: 语音转写与说话人识别")
    logger.info("=" * 60)
    
    transcripts = []
    for i, (link, audio_path) in enumerate(zip(links, downloaded_files), 1):
        url = link['url']
        if audio_path is None:
            transcripts.append(None)
            continue
        
        if not args.force and progress_manager.get_status(url) in ['completed', 'transcribed']:
            logger.info(f"[{i}/{len(links)}] 跳过已转写: {url}")
            transcripts.append(progress_manager.get_transcript(url))
            continue
        
        try:
            logger.info(f"[{i}/{len(links)}] 正在转写音频: {audio_path}")
            transcript = transcriber.transcribe(audio_path, link.get('platform'))
            transcripts.append(transcript)
            progress_manager.update_status(url, 'transcribed', transcript=transcript)
            logger.info(f"  ✓ 转写完成，共 {len(transcript)} 个片段")
        except Exception as e:
            logger.error(f"  ✗ 转写失败: {e}")
            progress_manager.update_status(url, 'failed', error=str(e))
            transcripts.append(None)
    
    # 第四步：生成逐字稿和汇总报告
    logger.info("\n" + "=" * 60)
    logger.info("步骤 4/4: 生成逐字稿文档")
    logger.info("=" * 60)
    
    for i, (link, transcript) in enumerate(zip(links, transcripts), 1):
        if transcript is None:
            continue
        
        url = link['url']
        if not args.force and progress_manager.get_status(url) == 'completed':
            logger.info(f"[{i}/{len(links)}] 跳过已完成: {url}")
            continue
        
        try:
            metadata = progress_manager.get_metadata(url) or {}
            output_path = reporter.generate_transcript(transcript, metadata, link)
            progress_manager.update_status(url, 'completed', transcript_path=output_path)
            logger.info(f"[{i}/{len(links)}] ✓ 逐字稿已生成: {output_path}")
        except Exception as e:
            logger.error(f"[{i}/{len(links)}] ✗ 生成逐字稿失败: {e}")
    
    # 生成处理结果汇总
    reporter.generate_summary_report(progress_manager, 'data/processing_result.xlsx')
    
    logger.info("\n" + "=" * 60)
    logger.info("处理完成！")
    logger.info("=" * 60)
    logger.info(f"元数据表格: data/links_summary.xlsx")
    logger.info(f"处理结果: data/processing_result.xlsx")
    logger.info(f"音频文件: data/downloads/")
    logger.info(f"逐字稿: data/transcripts/")


if __name__ == '__main__':
    main()