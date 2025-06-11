'''
Author: Leili
Date: 2025-05-06
LastEditors: Leili
LastEditTime: 2025-06-11 10:23:48
FilePath: /GoogleModelProcess/Scripts/utils.py
Description: 通用函数
'''

def remove_chinese_chars(text):
    """
    去除字符串中的所有中文字符
    参数:
        text: 输入字符串
    返回:
        去除中文字符后的字符串
    实现原理:
        1. 使用正则表达式匹配所有Unicode中文字符范围
        2. 将这些字符替换为空字符串
    """
    import re
    # 匹配所有中文字符的正则表达式
    # 包括基本汉字(4E00-9FFF)、扩展A区(3400-4DBF)、扩展B区(20000-2A6DF)等
    pattern = re.compile('[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf]')
    return pattern.sub('', text)

def get_filename(address):
    """
    根据地址生成规范化文件名
    
    功能:
        1. 从配置文件中获取地址信息
        2. 去除地址中的中文字符
        3. 替换特殊字符为下划线
        4. 生成适合作为文件名的字符串
    
    参数:
        address: str - 原始地址字符串，如果为None则从配置文件获取
    
    返回:
        str: 处理后的规范化文件名
    
    异常:
        无显式抛出异常，但依赖的get_setting和remove_chinese_chars函数可能抛出异常
    
    示例:
        >>> get_filename("110 N La Brea Ave, Inglewood, CA 90301")
        '110_N_La_Brea_Ave_Inglewood_CA_90301'
    """
    # 从配置文件获取地址
    filename = remove_chinese_chars(address.replace(' ', '_').replace(",", "")).replace("|", "").replace(".", "").replace("/", "_").replace("\\", "_")
    return filename