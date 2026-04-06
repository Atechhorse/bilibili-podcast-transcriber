"""
日志配置
"""
import logging
import sys
from pathlib import Path


def setup_logger(name: str) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    # 文件输出
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(
        log_dir / 'app.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger