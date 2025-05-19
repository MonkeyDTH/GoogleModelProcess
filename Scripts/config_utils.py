'''
Author: Leili
Date: 2025-05-06
LastEditors: Leili
LastEditTime: 2025-05-19 16:25:09
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

def set_setting(setting_name, value):
    """
    设置配置项的值
    
    功能:
        1. 修改或添加Settings节中的配置项
        2. 自动保存修改后的配置文件
    
    参数:
        setting_name: str - 要设置的配置项名称
        value: str - 要设置的配置值
    
    返回:
        bool: 设置是否成功
    
    异常:
        configparser.Error: 当配置文件操作失败时抛出
        IOError: 当文件写入失败时抛出
    """
    try:
        config = load_config()
        
        # 确保Settings节存在
        if not config.has_section('Settings'):
            config.add_section('Settings')
            
        # 设置配置项
        config.set('Settings', setting_name, str(value))
        
        # 保存修改
        with open(get_config_path(), 'w', encoding='utf-8') as configfile:
            config.write(configfile)
            
        return True
        
    except (configparser.Error, IOError) as e:
        print(f"设置配置项失败: {str(e)}")
        return False

def get_log_level():
    """获取日志级别配置"""
    config = load_config()
    return config.get('Logging', 'log_level', fallback='info')

def get_log_dir():
    """获取日志目录配置"""
    config = load_config()
    return config.get('Logging', 'log_dir', fallback=None)
