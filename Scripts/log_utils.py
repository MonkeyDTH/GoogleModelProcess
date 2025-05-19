'''
Author: Leili
Date: 2025-05-06
LastEditors: Leili
LastEditTime: 2025-05-19 14:38:43
FilePath: /GoogleModelProcess/Scripts/log_utils.py
Description: 日志工具模块，提供统一的日志记录功能
'''
import os
import logging
import sys
from datetime import datetime
from pathlib import Path

# 日志级别映射
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

# 全局日志记录器
logger = None

def setup_logger(log_level='info', log_dir=None, log_file=None, b_print_info=True):
    """
    设置日志记录器
    
    Args:
        log_level: 日志级别，可选值：debug, info, warning, error, critical
        log_dir: 日志目录，默认为项目根目录下的logs文件夹
        log_file: 日志文件名，默认为当前日期的日志文件
    
    Returns:
        logger: 日志记录器对象
    """
    global logger
    
    if logger is not None:
        return logger
    
    # 获取项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    
    # 设置日志目录
    if log_dir is None:
        log_dir = os.path.join(project_dir, 'logs')
    
    # 确保日志目录存在
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 设置日志文件名
    if log_file is None:
        current_date = datetime.now().strftime('%Y%m%d')
        log_file = f'google_model_process_{current_date}.log'
    
    log_path = os.path.join(log_dir, log_file)
    
    # 创建日志记录器
    logger = logging.getLogger('google_model_process')
    logger.setLevel(LOG_LEVELS.get(log_level.lower(), logging.INFO))
    
    # 防止重复添加处理器
    if not logger.handlers:
        # 创建文件处理器
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(LOG_LEVELS.get(log_level.lower(), logging.INFO))
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(LOG_LEVELS.get(log_level.lower(), logging.INFO))
        
        # 设置日志格式
        log_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(log_format)
        console_handler.setFormatter(log_format)
        
        # 添加处理器到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    if b_print_info:
        logger.info(f"日志系统初始化完成，日志文件: {log_path}")
    return logger

def get_logger():
    """
    获取日志记录器
    
    Returns:
        logger: 日志记录器对象
    """
    global logger
    if logger is None:
        logger = setup_logger()
    return logger

# 便捷日志记录函数
def logD(message):
    """记录调试级别日志"""
    get_logger().debug(message)

def logI(message):
    """记录信息级别日志"""
    get_logger().info(message)

def logW(message):
    """记录警告级别日志"""
    get_logger().warning(message)

def logE(message):
    """记录错误级别日志"""
    get_logger().error(message)

def critical(message):
    """记录严重错误级别日志"""
    get_logger().critical(message)

def logEX(message):
    """记录异常信息，包含堆栈跟踪"""
    get_logger().exception(message)