'''
Author: Leili
Date: 2025-04-27 15:27:27
LastEditors: Leili
LastEditTime: 2025-04-29 10:37:04
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

def activate_window(title):
    """
    激活包含"Google Chrome Gpu"的窗口
    """
    # 在Windows上使用pygetwindow查找窗口
    try:
        import pygetwindow as gw
        # 尝试查找包含"Google Chrome Gpu"的窗口
        chrome_gpu_windows = gw.getWindowsWithTitle(title)
        
        if chrome_gpu_windows:
            # 激活找到的第一个窗口
            window = chrome_gpu_windows[0]
            if not window.isActive:
                window.activate()
            print(f"已激活窗口: {window.title}")
            time.sleep(0.5)  # 给窗口激活一点时间
            return True
        else:
            print("未找到Google Chrome Gpu窗口")
            return False
            
    except ImportError:
        print("请安装pygetwindow: pip install pygetwindow")
        return False

def launch_renderdoc_and_inject():
    """
    启动RenderDoc并点击File菜单，然后点击Inject into Process并选择指定进程
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
        
        # 增加初始等待时间
        time.sleep(3)
        
        try:
            from pywinauto.application import Application
            from pywinauto.timings import wait_until, Timings
            from pywinauto import keyboard  # 使用pywinauto的keyboard
            import win32gui
            import win32con
            import pyautogui  # 添加pyautogui导入
            
            # 增加默认超时时间
            Timings.window_find_timeout = 30
            Timings.app_connect_timeout = 30
            Timings.exists_timeout = 30
            
            # 尝试多次连接到RenderDoc窗口
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"尝试第{attempt + 1}次连接RenderDoc窗口...")
                    app = Application(backend="uia").connect(path=renderdoc_path, timeout=20)
                    main_window = app.window(title_re=".*RenderDoc.*")
                    main_window.wait('visible', timeout=20)
                    print("成功连接到RenderDoc窗口")
                    
                    # 获取窗口句柄
                    hwnd = main_window.handle
                    
                    # 调整窗口大小和位置
                    target_width = 1600  # 修改为1600
                    target_height = 900  # 修改为900
                    screen_width = pyautogui.size()[0]
                    screen_height = pyautogui.size()[1]
                    new_left = max(0, int((screen_width - target_width) / 2))
                    new_top = max(0, int((screen_height - target_height) / 2))
                    
                    # 调整窗口大小
                    win32gui.MoveWindow(hwnd, new_left, new_top, target_width, target_height, True)
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(2)
                    
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"连接失败: {str(e)}，等待5秒后重试...")
                        time.sleep(5)
                    else:
                        raise Exception("无法连接到RenderDoc窗口，请确保程序已正确启动")
            
            # 点击File菜单
            print("尝试点击File菜单...")
            keyboard.send_keys("%{F}")  # Alt+F
            time.sleep(2)
            
            # 选择Inject into Process
            print("尝试选择Inject into Process...")
            keyboard.send_keys("I")  # 选择Inject into Process
            time.sleep(1)
            keyboard.send_keys("{ENTER}")
            time.sleep(1)
            
            # 先点击进程列表以确保焦点在列表上
            print("尝试搜索Google Chrome Gpu进程...")
            pyautogui.moveTo(new_left + 80, new_top + 550, duration=0.1)  # 调整坐标
            pyautogui.click()
            time.sleep(0.5)
            
            # 输入搜索内容
            pyautogui.write('Google  Chrome  Gpu', interval=0.03)  # 使用write方法, 用中文输入法需要打两个空格
            time.sleep(1)

            # 在进程选择对话框中点击
            print("尝试在进程列表中选择Chrome GPU进程...")
            # 点击搜索到的第一个进程
            pyautogui.moveTo(new_left + 80, new_top + 275, duration=0.1)  # 调整坐标
            pyautogui.click()
            time.sleep(0.5)
            
            # 按回车确认搜索
            keyboard.send_keys('{ENTER}')
            time.sleep(1)

            # 等待注入完成
            activate_window("Google Chrome Gpu")
            time.sleep(1)

            # 按回车确认进入
            keyboard.send_keys('{ENTER}')
            time.sleep(1)
            
            print("已完成注入操作")
            return True
            
        except ImportError:
            print("请先安装必要的库: pip install pywinauto pyautogui")
            return False
        except Exception as e:
            print(f"操作RenderDoc窗口时发生错误: {str(e)}")
            return False
            
    except Exception as e:
        print(f"启动RenderDoc时发生错误: {str(e)}")
        return False

def capture_frame():
    """
    截取当前屏幕并保存为PNG文件
    """
    try:
        # 切换到Chrome窗口
        activate_window("Google Chrome")
        time.sleep(1)
    except Exception as e:
        print(f"截取帧时发生错误: {str(e)}")
        return False


if __name__ == "__main__":
    # 设置建筑地址
    address = "10912 Yukon Ave S"
    
    try:
        # 获取经纬度
        lat, lng = get_coordinates_from_google(address, API_KEY)
        print(f"地址: {address}")
        print(f"经纬度: ({lat}, {lng})")
        
        # 执行启动并获取进程ID
        chrome_pids = get_chrome_pid(lat, lng)
        # 启动RenderDoc
        launch_renderdoc_and_inject()
        # 截取帧
        capture_frame()
        
    except Exception as e:
        print(f"错误: {str(e)}")