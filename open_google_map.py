'''
Author: Leili
Date: 2025-04-27 15:27:27
LastEditors: Leili
LastEditTime: 2025-04-27 15:51:53
FilePath: /GoogleModelProcess/open_google_map.py
Description: 
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import time

# 指定经纬度和缩放
lat = 33.93643011099182
lng = -118.33465519884332
zoom = 19

# 直接使用卫星视图的URL
url = f'https://www.google.com/maps/@{lat},{lng},{zoom}z/data=!3m1!1e3'

# 启动Chrome（需提前安装chromedriver且版本匹配）
driver = webdriver.Chrome()
driver.get(url)

# 等待页面加载完成
wait = WebDriverWait(driver, 10)

try:
    # 等待地图加载完成
    time.sleep(5)
    
    print("已打开卫星地图视图，按 Ctrl+C 可关闭浏览器，或直接关闭浏览器窗口退出...")
    
    # 保持浏览器窗口打开，并检查浏览器是否被关闭
    while True:
        try:
            # 尝试获取当前窗口句柄，如果浏览器被关闭会抛出异常
            driver.current_window_handle
            time.sleep(1)
        except WebDriverException:
            print("浏览器窗口已被关闭，程序退出...")
            break
except KeyboardInterrupt:
    print("正在关闭浏览器...")
except Exception as e:
    print(f"发生错误: {str(e)}")
finally:
    try:
        driver.quit()
    except:
        pass