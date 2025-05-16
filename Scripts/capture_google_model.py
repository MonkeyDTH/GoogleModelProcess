'''
Author: Leili
Date: 2025-04-27 15:27:27
LastEditors: Leili
LastEditTime: 2025-05-16 14:25:43
FilePath: /GoogleModelProcess/Scripts/capture_google_model.py
Description: 
'''
import os
import subprocess
import time
import psutil
import googlemaps
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
if project_dir not in sys.path:
    sys.path.append(project_dir)

# 导入配置工具和日志工具
from Scripts.config_utils import get_api_key, get_path, get_setting, get_log_level, get_log_dir
from Scripts.log_utils import setup_logger, logD, logI, logW, logE, logEX

# 初始化日志系统
logger = setup_logger(log_level=get_log_level(), log_dir=get_log_dir())

# 从配置文件获取 Google Maps API 密钥
API_KEY = get_api_key()

def get_coordinates_from_google(address, api_key=None):
    """
    使用Google Maps API获取地址的经纬度
    :param address: 地址字符串
    :param api_key: Google Maps API密钥，如果为None则使用配置文件中的密钥
    :return: (纬度, 经度)元组
    """
    # 如果未提供API密钥，则使用配置文件中的密钥
    if api_key is None:
        api_key = API_KEY
    
    # 创建Google Maps客户端
    gmaps = googlemaps.Client(key=api_key)
    
    # 地理编码
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            lat, lng = location['lat'], location['lng']
            return lat, lng
        else:
            logE(f"获取经纬度失败，无法找到该地址: {address}")
            raise ValueError("无法找到该地址")
    except Exception as e:
        logEX(f"Google Maps API错误: {str(e)}")
        raise Exception(f"Google Maps API错误: {str(e)}")

def launch_chrome_google_map(lat=None, lng=None, zoom=None):
    """
    打开指定经纬度的Google地图
    :param lat: 纬度
    :param lng: 经度
    :param zoom: 缩放级别
    """
    # 如果未提供缩放级别，则从配置文件获取
    if zoom is None:
        zoom = int(get_setting('map_zoom', 21))
    
    logD(f"准备打开Google地图，经纬度: ({lat}, {lng})，缩放级别: {zoom}")
    
    # 构建卫星视图的URL
    url = f'https://www.google.com/maps/@{lat},{lng},{zoom}z/data=!3m1!1e3'
    logD(f"Google地图URL: {url}")
    
    # 从配置文件获取Chrome路径
    chrome_path = get_path('chrome_path')
    
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
            
            logD(f"Chrome启动命令: {' '.join(cmd)}")
            
            # 直接启动Chrome，不通过cmd.exe
            process = subprocess.Popen(cmd, env=env)
            logI(f"已打开卫星地图视图，Chrome进程ID: {process.pid}")
            
            # 等待新的Chrome进程启动
            time.sleep(2)
            
            if process.pid:
                logI(f"新启动的Chrome主进程ID: {process.pid}")
                return {process.pid}
            else:
                logW("未能检测到新的Chrome主进程")
                return set()
                
        except Exception as e:
            logEX(f"启动Chrome时发生错误: {str(e)}")
            return set()
    else:
        logE(f"未找到Chrome浏览器: {chrome_path}")
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
            logD(f"已激活窗口: {window.title}")
            time.sleep(0.5)  # 给窗口激活一点时间
            return True
        else:
            logE(f"未找到{title}窗口")
            return False
            
    except ImportError:
        logE("请安装pygetwindow: pip install pygetwindow")
        return False

def launch_renderdoc_and_inject():
    """
    启动RenderDoc并点击File菜单，然后点击Inject into Process并选择指定进程
    """
    # 从配置文件获取RenderDoc路径
    renderdoc_path = get_path('renderdoc_path')
    
    if not os.path.exists(renderdoc_path):
        logEX(f"未找到RenderDoc: {renderdoc_path}")
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
        logI(f"已启动RenderDoc")
        
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
                    logD(f"尝试第{attempt + 1}次连接RenderDoc窗口...")
                    app = Application(backend="uia").connect(path=renderdoc_path, timeout=20)
                    main_window = app.window(title_re=".*RenderDoc.*")
                    main_window.wait('visible', timeout=20)
                    logD("成功连接到RenderDoc窗口")
                    
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
                        logW(f"连接失败: {str(e)}，等待5秒后重试...")
                        time.sleep(5)
                    else:
                        raise Exception("无法连接到RenderDoc窗口，请确保程序已正确启动")
            
            # 点击File菜单
            logD("尝试点击File菜单...")
            keyboard.send_keys("%{F}")  # Alt+F
            time.sleep(2)
            
            # 选择Inject into Process
            logD("尝试选择Inject into Process...")
            keyboard.send_keys("I")  # 选择Inject into Process
            time.sleep(1)
            keyboard.send_keys("{ENTER}")
            time.sleep(1)
            
            # 先点击进程列表以确保焦点在列表上
            logD("尝试搜索Google Chrome Gpu进程...")
            pyautogui.moveTo(new_left + 80, new_top + 550, duration=0.1)  # 调整坐标
            pyautogui.click()
            time.sleep(0.5)
            
            # 输入搜索内容
            pyautogui.write('Google  Chrome  Gpu', interval=0.05)  # 使用write方法, 用中文输入法需要打两个空格
            time.sleep(1)

            # 在进程选择对话框中点击
            logD("尝试在进程列表中选择Chrome GPU进程...")
            # 点击搜索到的第一个进程
            pyautogui.moveTo(new_left + 80, new_top + 275, duration=0.1)  # 调整坐标
            pyautogui.click()
            time.sleep(0.5)
            
            # 按回车确认搜索
            keyboard.send_keys('{ENTER}')
            time.sleep(1)

            # 等待注入完成
            if not activate_window("Google Chrome Gpu"):
                return False
            time.sleep(1)

            # 按回车确认进入
            keyboard.send_keys('{ENTER}')
            time.sleep(1)
            
            logI("已完成注入操作")
            return True
            
        except ImportError:
            logE("请先安装必要的库: pip install pywinauto pyautogui")
            return False
        except Exception as e:
            logE(f"操作RenderDoc窗口时发生错误: {str(e)}")
            return False
            
    except Exception as e:
        logEX(f"启动RenderDoc时发生错误: {str(e)}")
        return False

def capture_frame(filename=None):
    """
    截取当前屏幕到RenderDoc中
    
    参数:
        filename: 预先计算好的文件名，如果提供则直接使用
    """
    try:
        # 切换到Chrome窗口
        activate_window("Google Chrome")
        time.sleep(1)
        
        # 导入pyautogui
        import pyautogui
        
        # 获取屏幕尺寸
        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        
        # 移动到屏幕中心
        pyautogui.moveTo(center_x, center_y, duration=0.5)
        
        # 按下鼠标左键
        pyautogui.mouseDown()
        time.sleep(0.5)
        
        for _ in range(2):
            duration = 0.3
            # 向左移动
            pyautogui.moveTo(center_x - 200, center_y, duration=duration)
            pyautogui.moveTo(center_x, center_y, duration=duration)
            
            # 向右移动
            pyautogui.moveTo(center_x + 200, center_y, duration=duration)
            pyautogui.moveTo(center_x, center_y, duration=duration)
            
            # 向上移动
            pyautogui.moveTo(center_x, center_y - 200, duration=duration)
            pyautogui.moveTo(center_x, center_y, duration=duration)
            
            # 向下移动
            pyautogui.moveTo(center_x, center_y + 200, duration=duration)
            pyautogui.moveTo(center_x, center_y, duration=duration)

        # 按F12截图
        pyautogui.press('f12')
        time.sleep(1)

        # 释放鼠标左键
        pyautogui.mouseUp()
        time.sleep(0.5)
        logI("已完成鼠标移动和截图操作")

        # 切换到RenderDoc窗口
        activate_window("RenderDoc")
        time.sleep(1)

        # 处理文件名
        if filename:
            # 直接使用预先计算好的文件名
            save_filename = filename
            logI(f"使用预先计算的文件名保存RDC: {save_filename}")
        else:
            # 如果没有提供地址和文件名，使用时间戳
            from datetime import datetime
            save_filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logI(f"未提供地址或文件名，使用时间戳文件名: {save_filename}")

        # 保存截取结果
        pyautogui.moveTo(1275, 1100, duration=0.3)
        pyautogui.click()
        pyautogui.rightClick()
        time.sleep(0.3)
        pyautogui.moveTo(1300, 1155, duration=0.3)
        pyautogui.click()
        time.sleep(3)

        # # 确保切换到英文输入法
        # try:
        #     import win32api
        #     import win32con
        #     # 设置为英文输入法（美国英语）
        #     win32api.LoadKeyboardLayout('00000409', win32con.KLF_ACTIVATE)
        #     logI("已切换到英文输入法")
        # except ImportError:
        #     logW("未安装win32api，使用快捷键切换输入法")
        
        # 清空当前输入框内容（以防有默认文本）
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        time.sleep(0.3)
        
        # 输入文件名（使用interval参数确保字符输入正确）
        logI(f"正在输入文件名: {save_filename}")
        pyautogui.press('shift')
        time.sleep(0.5)
        pyautogui.write(save_filename, interval=0.05)  # 增加输入间隔，提高可靠性
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(0.5)  # 增加等待时间
        
        # TODO:处理可能出现的覆盖确认对话框
        
        # 返回完整的文件路径，用于后续检查
        save_dir = get_path('rdc_dir')
        if save_dir:
            full_path = os.path.join(save_dir, f"{save_filename}.rdc")
        else:
            # 如果没有指定保存目录，则使用默认位置（通常是用户的"Documents"文件夹）
            full_path = f"{save_filename}.rdc"  # 这里只返回文件名，因为不确定默认保存位置
            
        logI(f"RDC文件已保存: {full_path}")
        return full_path
        
    except Exception as e:
        logE(f"截取帧时发生错误: {str(e)}")
        return False

def check_rdc_file_exists(rdc_file_path=None):
    """
    检查RDC文件是否存在
    
    参数:
        rdc_file_path: RDC文件的完整路径
    
    返回:
        bool: 文件是否存在
    """
    # 检查文件是否存在
    if os.path.exists(rdc_file_path):
        logI(f"找到RDC文件: {rdc_file_path}")
        return True
    else:
        logW(f"未找到RDC文件: {rdc_file_path}")
        return False

def open_blender():
    """
    打开Blender并执行内部脚本
    """
    try:
        # 获取当前脚本目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Blender脚本路径
        blender_script_path = os.path.join(current_dir, "blender_script.py")
        
        # 检查脚本是否存在
        if not os.path.exists(blender_script_path):
            logE(f"错误: Blender脚本不存在: {blender_script_path}")
            return False
        
        # 从配置文件获取Blender路径
        blender_path = get_path('blender_path')
        if not os.path.exists(blender_path):
            logE(f"未找到Blender: {blender_path}")
            return False
            
        try:
            # 构建启动命令，添加--python参数执行脚本
            cmd = [
                blender_path,
                '--python', blender_script_path
            ]

            # 启动Blender并执行脚本
            print(f"正在启动Blender并执行脚本: {blender_script_path}")
            process = subprocess.Popen(cmd)
            print(f"已启动Blender进程，PID: {process.pid}")
            
            # 等待Blender启动和脚本执行完成
            signal_file = os.path.join(project_dir, "blender_script_done.signal")
            
            # 如果存在旧的信号文件，先删除
            if os.path.exists(signal_file):
                os.remove(signal_file)
            
            # 等待信号文件出现
            max_wait_time = 300  # 最长等待5分钟
            start_time = time.time()
            
            while not os.path.exists(signal_file):
                if time.time() - start_time > max_wait_time:
                    print("等待Blender脚本执行超时")
                    return False
                    
                print("等待Blender脚本执行完成...")
                time.sleep(5)
            
            # 删除信号文件
            os.remove(signal_file)
            logI("Blender脚本执行完成，继续执行后续步骤")
            
            return True

        except Exception as e:
            logEX(f"启动Blender时发生错误: {str(e)}")
            return False

    except Exception as e:
        print(f"运行Blender时发生错误: {str(e)}")
        return False

def match_template():
    """
    使用特征点匹配方法查找图像中的目标
    """
    try:
        # 切换到Blender窗口
        activate_window("Blender")
        time.sleep(1)
        
        # 导入必要的库
        import cv2
        import numpy as np
        import pyautogui
        import os
        from datetime import datetime
        
        # 从配置文件获取模板图片路径
        template_path = get_path('template_image_path')
        
        if not os.path.exists(template_path):
            print(f"未找到模板图片: {template_path}")
            return False
            
        # 截取当前屏幕
        print("正在截取当前屏幕...")
        screenshot = pyautogui.screenshot()
        
        # 创建保存截图的目录
        save_dir = os.path.join(os.getcwd(), "screenshots")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 生成时间戳文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(save_dir, f"screenshot_{timestamp}.png")
        
        # 保存截图
        screenshot.save(screenshot_path)
        print(f"截图已保存至: {screenshot_path}")
        
        # 读取模板图片和截图
        template = cv2.imread(template_path)
        screenshot_cv = cv2.imread(screenshot_path)
        
        # 检查图片是否正确加载
        if template is None or screenshot_cv is None:
            print("无法加载图片，请检查图片路径")
            return False
            
        # 转换为灰度图
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        screenshot_gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        # 尝试使用SIFT特征检测器
        try:
            print("尝试使用SIFT特征检测器...")
            sift = cv2.SIFT_create()
            
            # 在模板和截图中检测关键点和描述符
            kp1, des1 = sift.detectAndCompute(template_gray, None)
            kp2, des2 = sift.detectAndCompute(screenshot_gray, None)
            
            # 使用FLANN匹配器进行特征匹配
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            
            # 获取匹配结果
            matches = flann.knnMatch(des1, des2, k=2)
            
            # 应用Lowe's比率测试筛选好的匹配
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
            
            print(f"SIFT找到 {len(good_matches)} 个良好匹配点")
            
            # 如果找到足够的好匹配点，处理匹配结果
            min_match_count = 10
            if len(good_matches) >= min_match_count:
                return process_matches(good_matches, kp1, kp2, template_gray, screenshot_cv, template, 
                                      template_path, screenshot_path, timestamp, save_dir, "SIFT")
            else:
                print("SIFT匹配点不足，尝试使用ORB特征检测器...")
        except Exception as e:
            print(f"SIFT特征检测失败: {str(e)}，尝试使用ORB特征检测器...")
        
        # 尝试使用ORB特征检测器
        try:
            print("使用ORB特征检测器...")
            orb = cv2.ORB_create(nfeatures=1000)
            
            # 在模板和截图中检测关键点和描述符
            kp1, des1 = orb.detectAndCompute(template_gray, None)
            kp2, des2 = orb.detectAndCompute(screenshot_gray, None)
            
            # 使用暴力匹配器进行特征匹配
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            
            # 获取匹配结果
            matches = bf.match(des1, des2)
            
            # 按距离排序
            matches = sorted(matches, key=lambda x: x.distance)
            
            # 选择前N个最佳匹配
            good_matches = matches[:50] if len(matches) > 50 else matches
            
            print(f"ORB找到 {len(good_matches)} 个良好匹配点")
            
            # 如果找到足够的好匹配点，处理匹配结果
            min_match_count = 10
            if len(good_matches) >= min_match_count:
                return process_matches(good_matches, kp1, kp2, template_gray, screenshot_cv, template, 
                                      template_path, screenshot_path, timestamp, save_dir, "ORB")
            else:
                print("ORB匹配点不足，无法找到目标")
                return False
        except Exception as e:
            print(f"ORB特征检测失败: {str(e)}")
            return False
            
    except Exception as e:
        print(f"模板匹配过程中发生错误: {str(e)}")
        return False

def process_matches(good_matches, kp1, kp2, template_gray, screenshot_cv, template, 
                   template_path, screenshot_path, timestamp, save_dir, method_name):
    """
    处理特征匹配结果，计算目标位置并保存结果
    
    参数:
        good_matches: 良好的特征匹配点列表
        kp1: 模板图像的关键点
        kp2: 截图的关键点
        template_gray: 灰度模板图像
        screenshot_cv: 截图的OpenCV格式
        template: 原始模板图像
        template_path: 模板图像路径
        screenshot_path: 截图路径
        timestamp: 时间戳
        save_dir: 保存目录
        method_name: 使用的特征检测方法名称
    
    返回:
        bool: 处理是否成功
    """
    import cv2
    import numpy as np
    import os
    
    try:
        print(f"正在处理{method_name}特征匹配结果...")
        
        # 提取匹配点的坐标
        if method_name == "SIFT":
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        else:  # ORB
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        # 计算单应性矩阵
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()
        
        # 获取模板图像的尺寸
        h, w = template_gray.shape
        
        # 定义模板图像的四个角点
        pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
        
        # 使用单应性矩阵转换角点坐标
        dst = cv2.perspectiveTransform(pts, M)
        
        # 计算目标中心点
        center_x = int(np.mean(dst[:, 0, 0]))
        center_y = int(np.mean(dst[:, 0, 1]))
        
        # 在结果图上绘制边界框
        result_image = screenshot_cv.copy()
        cv2.polylines(result_image, [np.int32(dst)], True, (0, 255, 0), 3)
        
        # 在结果图上标记中心点
        cv2.circle(result_image, (center_x, center_y), 10, (0, 0, 255), -1)
        
        print(f"找到目标: 中心坐标 = ({center_x}, {center_y})")
        
        # 绘制匹配结果
        if method_name == "SIFT":
            draw_params = dict(
                matchColor=(0, 255, 0),
                singlePointColor=None,
                matchesMask=matchesMask,
                flags=2
            )
            match_img = cv2.drawMatches(template, kp1, screenshot_cv, kp2, good_matches, None, **draw_params)
        else:  # ORB
            draw_params = dict(
                matchColor=(0, 255, 0),
                singlePointColor=None,
                flags=2
            )
            match_img = cv2.drawMatches(template, kp1, screenshot_cv, kp2, good_matches, None, **draw_params)
        
        # 保存结果图
        result_path = os.path.join(save_dir, f"match_result_{method_name}_{timestamp}.png")
        cv2.imwrite(result_path, result_image)
        
        # 保存匹配点图
        matches_path = os.path.join(save_dir, f"matches_{method_name}_{timestamp}.png")
        cv2.imwrite(matches_path, match_img)
        
        print(f"匹配结果已保存至: {result_path}")
        print(f"匹配点图已保存至: {matches_path}")
        
        # 将匹配结果保存到文本文件
        result_txt_path = os.path.join(save_dir, f"match_coordinates_{method_name}_{timestamp}.txt")
        with open(result_txt_path, 'w') as f:
            f.write(f"模板图片: {template_path}\n")
            f.write(f"截图时间: {timestamp}\n")
            f.write(f"匹配方法: {method_name}特征点匹配\n")
            f.write(f"良好匹配点数量: {len(good_matches)}\n\n")
            f.write(f"目标中心坐标: ({center_x}, {center_y})\n")
            f.write(f"目标边界框坐标:\n")
            for i, point in enumerate(np.int32(dst)):
                f.write(f"  点{i+1}: ({point[0][0]}, {point[0][1]})\n")
        
        print(f"匹配坐标已保存至: {result_txt_path}")
        
        # 获取目标边界框的四个角点坐标
        points = np.int32(dst).reshape(4, 2)
        
        # 返回匹配结果
        return {
            "success": True,
            "center": (center_x, center_y),
            "points": points.tolist(),
            "method": method_name
        }
        
    except Exception as e:
        print(f"处理{method_name}匹配结果时发生错误: {str(e)}")
        return False

def terminate_processes(process_names):
    """
    终止指定名称的进程
    
    参数:
        process_names (dict): 进程名称和匹配方式的字典，格式为 {进程名: 是否使用部分匹配}
                             例如: {'chrome.exe': False, 'renderdoc': True}
                             False表示精确匹配，True表示部分匹配
    
    返回:
        bool: 是否成功终止所有指定进程
    """
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            for proc_name, partial_match in process_names.items():
                try:
                    if (partial_match and proc_name.lower() in proc.name().lower()) or \
                       (not partial_match and proc.name().lower() == proc_name.lower()):
                        proc.terminate()
                        logD(f"已终止{proc.name()}进程: {proc.pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logW(f"无法终止进程 {proc.name()} (PID: {proc.pid}): {str(e)}")
                    continue
                    
        # 等待进程完全关闭
        time.sleep(2)
        return True
    except Exception as e:
        logW(f"关闭进程时发生错误: {str(e)}")
        return False

def clear_processes():
    """
    关闭所有相关进程: Chrome, RenderDoc, Blender
    """
    terminate_processes({'chrome.exe': False, 'renderdoc': True})
    try:
        # 终止Chrome和RenderDoc进程
        process_names = {
            'chrome.exe': False,    # 精确匹配
            'renderdoc': True,      # 部分匹配
            'Blender': True         # 部分匹配
        }
        terminate_processes(process_names)
    except Exception as e:
        logW(f"关闭进程时发生错误: {str(e)}")


if __name__ == "__main__":
    # 设置建筑地址
    # address = "10912 Yukon Ave S"
    
    # 从配置文件获取地址
    address = get_setting('address')
    filename = address.replace(' ', '_')
    
    try:
        clear_processes()
        b_capture = True
        if b_capture:
            # 获取经纬度
            lat, lng = get_coordinates_from_google(address, API_KEY)
            logI(f"地址: {address}, 经纬度: ({lat}, {lng})")
            
            # 执行启动并获取进程ID
            chrome_pids = launch_chrome_google_map(lat, lng)
            # 启动RenderDoc
            if not launch_renderdoc_and_inject():
                raise RuntimeError("启动RenderDoc或注入失败")
            # 截取帧
            rdc_fname = os.path.join(get_path('rdc_dir'), f"{filename}.rdc")
            if os.path.exists(rdc_fname):
                os.remove(rdc_fname)
            capture_frame(filename)

            time.sleep(1)
            if not check_rdc_file_exists(rdc_fname):
                clear_processes()
                raise RuntimeError("未找到RDC文件，无法继续处理")

        # 打开Blender
        open_blender()

        # 匹配模板
        match_template()

        # 清理进程
        clear_processes()
        
        
    except Exception as e:
        logEX(f"错误: {str(e)}")
        