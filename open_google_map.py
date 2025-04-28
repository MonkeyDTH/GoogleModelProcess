'''
Author: Leili
Date: 2025-04-27 15:27:27
LastEditors: Leili
LastEditTime: 2025-04-27 18:45:08
FilePath: /GoogleModelProcess/open_google_map.py
Description: 
'''
import os
import subprocess
import time
import psutil

# 指定经纬度和缩放
lat = 33.93631
lng = -118.33468
zoom = 21

# 构建卫星视图的URL
url = f'https://www.google.com/maps/@{lat},{lng},{zoom}z/data=!3m1!1e3'

# Chrome路径
chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

def get_chrome_pid():
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

def launch_renderdoc_and_inject(chrome_pid):
    """
    启动RenderDoc并设置注入到指定的Chrome进程
    Args:
        chrome_pid: Chrome浏览器的进程ID
    """
    # RenderDoc默认安装路径
    renderdoc_path = r'C:\Program Files\RenderDoc\qrenderdoc.exe'
    
    if not os.path.exists(renderdoc_path):
        print(f"未找到RenderDoc: {renderdoc_path}")
        return False
        
    try:
        # 构建PowerShell命令字符串
        powershell_command = f'Start-Process -FilePath "{renderdoc_path}" -ArgumentList "--inject-pid","{chrome_pid}","--capture-all" -Verb RunAs'
        
        # 构建启动命令
        cmd = [
            'powershell.exe',
            '-Command',
            powershell_command
        ]
        
        # 启动RenderDoc
        subprocess.Popen(cmd)
        print(f"已启动RenderDoc并设置注入到进程ID: {chrome_pid}")
        return True
        
    except Exception as e:
        print(f"启动RenderDoc时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 执行启动并获取进程ID
    chrome_pids = get_chrome_pid()
    
    # 如果成功获取到Chrome进程ID，则启动RenderDoc并注入
    if chrome_pids:
        for pid in chrome_pids:
            launch_renderdoc_and_inject(pid)
    
    # launch_renderdoc_and_inject(pid)