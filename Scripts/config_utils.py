'''
Author: Leili
Date: 2025-05-06
LastEditors: Leili
LastEditTime: 2025-05-06
FilePath: /GoogleModelProcess/Scripts/config_utils.py
Description: 配置文件读取工具
'''
import os
import configparser
from pathlib import Path

def get_config_path():
    """获取配置文件路径"""
    # 获取当前脚本所在目录
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    # 配置文件在项目根目录
    config_path = current_dir.parent / 'config.ini'
    return config_path

def load_config():
    """加载配置文件"""
    config = configparser.ConfigParser()
    config_path = get_config_path()
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    config.read(config_path, encoding='utf-8')
    return config

def get_api_key():
    """获取Google Maps API密钥"""
    config = load_config()
    return config.get('API', 'google_maps_api_key')

def get_path(path_name):
    """获取路径配置
    
    Args:
        path_name: 路径名称，如 'chrome_path', 'renderdoc_path' 等
    
    Returns:
        str: 路径字符串
    """
    config = load_config()
    return config.get('Paths', path_name)

def get_setting(setting_name, fallback=None):
    """获取设置项
    
    Args:
        setting_name: 设置项名称
        fallback: 默认值，如果设置项不存在
    
    Returns:
        设置项的值
    """
    config = load_config()
    return config.get('Settings', setting_name, fallback=fallback)