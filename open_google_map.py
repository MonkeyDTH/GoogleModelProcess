'''
Author: Leili
Date: 2025-04-27 15:27:27
LastEditors: Leili
LastEditTime: 2025-04-27 15:55:17
FilePath: /GoogleModelProcess/open_google_map.py
Description: 
'''
import os
import subprocess
import winreg

# 指定经纬度和缩放
lat = 33.93643011099182
lng = -118.33465519884332
zoom = 21

# 构建卫星视图的URL
url = f'https://www.google.com/maps/@{lat},{lng},{zoom}z/data=!3m1!1e3'

def get_chrome_path():
    try:
        # 尝试从注册表获取Chrome路径
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
        chrome_path = winreg.QueryValue(key, None)
        winreg.CloseKey(key)
        return chrome_path
    except WindowsError:
        # 如果注册表查找失败，尝试常见安装路径
        paths = [
            os.path.expandvars(r'%PROGRAMFILES%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe'),
            os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe')
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    return None

chrome_path = get_chrome_path()

if chrome_path:
    try:
        # 启动Chrome并打开URL
        subprocess.Popen([chrome_path, url])
        print(f"已打开卫星地图视图，请在浏览器中查看...")
    except Exception as e:
        print(f"启动Chrome时发生错误: {str(e)}")
else:
    print("未找到Chrome浏览器，请确保Chrome已安装。")