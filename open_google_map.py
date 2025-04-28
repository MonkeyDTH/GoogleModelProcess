'''
Author: Leili
Date: 2025-04-27 15:27:27
LastEditors: Leili
LastEditTime: 2025-04-28 14:50:50
FilePath: /GoogleModelProcess/open_google_map.py
Description: 
'''
import os
import subprocess
import time
import psutil
import googlemaps

# Google Maps API密钥
API_KEY = "AIzaSyDLgBT4f31Oo509m9jAdm9Nlx-OOufXg7E"  # 请替换为您的API密钥

def get_coordinates_from_google(address, api_key):
    """
    使用Google Maps API获取地址的经纬度
    :param address: 地址字符串
    :param api_key: Google Maps API密钥
    :return: (纬度, 经度)元组
    """
    # 创建Google Maps客户端
    gmaps = googlemaps.Client(key=api_key)
    
    # 地理编码
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            raise ValueError("无法找到该地址")
    except Exception as e:
        raise Exception(f"Google Maps API错误: {str(e)}")

def get_chrome_pid(lat=None, lng=None, zoom=21):
    """
    打开指定经纬度的Google地图
    :param lat: 纬度
    :param lng: 经度
    :param zoom: 缩放级别
    """
    # 构建卫星视图的URL
    url = f'https://www.google.com/maps/@{lat},{lng},{zoom}z/data=!3m1!1e3'
    
    # Chrome路径
    chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    
    # 获取启动前的Chrome进程列表
    chrome_processes_before = {
        proc.pid: proc.cmdline() 
        for proc in psutil.process_iter(['pid', 'cmdline']) 
        if proc.name().lower() == 'chrome.exe'
    }
    
    if os.path.exists(chrome_path):
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['RENDERDOC_HOOK_EGL'] = '0'
            
            # 修改启动参数
            cmd = [
                chrome_path,
                '--disable-gpu-sandbox',
                '--gpu-startup-dialog',
                '--disable_direct_composition=1',
                url
            ]
            
            # 直接启动Chrome，不通过cmd.exe
            process = subprocess.Popen(cmd, env=env)
            print(f"已打开卫星地图视图，请在浏览器中查看...")
            
            # 等待新的Chrome进程启动
            time.sleep(2)
            
            if process.pid:
                print("新启动的Chrome主进程ID:", process.pid)
                return {process.pid}
            else:
                print("未能检测到新的Chrome主进程")
                return set()
                
        except Exception as e:
            print(f"启动Chrome时发生错误: {str(e)}")
            return set()
    else:
        print(f"未找到Chrome浏览器: {chrome_path}")
        return set()

def launch_renderdoc_and_inject():
    """
    启动RenderDoc
    """
    # RenderDoc默认安装路径
    renderdoc_path = r'C:\Program Files\RenderDoc\qrenderdoc.exe'
    
    if not os.path.exists(renderdoc_path):
        print(f"未找到RenderDoc: {renderdoc_path}")
        return False
        
    try:
        # 构建PowerShell命令字符串
        powershell_command = f'Start-Process -FilePath "{renderdoc_path}" -Verb RunAs'
        
        # 构建启动命令
        cmd = [
            'powershell.exe',
            '-Command',
            powershell_command
        ]
        
        # 启动RenderDoc
        subprocess.Popen(cmd)
        print(f"已启动RenderDoc")
        return True
        
    except Exception as e:
        print(f"启动RenderDoc时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 设置建筑地址
    address = "Coni’Seafood"
    
    try:
        # 获取经纬度
        lat, lng = get_coordinates_from_google(address, API_KEY)
        print(f"地址: {address}")
        print(f"经纬度: ({lat}, {lng})")
        
        # 执行启动并获取进程ID
        chrome_pids = get_chrome_pid(lat, lng)
        # 启动RenderDoc
        launch_renderdoc_and_inject()
        
    except Exception as e:
        print(f"错误: {str(e)}")