'''
Author: Leili
Date: 2025-04-29 16:30:00
LastEditors: Leili
LastEditTime: 2025-05-06
FilePath: /GoogleModelProcess/blender_script.py
Description: Blender内部操作脚本
'''
import bpy
import os
import sys
import time

# 添加项目根目录到Python路径，以便导入配置模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
if project_dir not in sys.path:
    sys.path.append(project_dir)

# 导入配置工具
from Scripts.config_utils import get_path

def main():
    """
    在Blender内部执行的主函数
    """
    print("开始执行Blender内部脚本...")
    
    try:
        # 删除场景中的所有物体
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        print("已删除场景中的所有物体")
        
        # 从配置文件获取RDC文件路径
        rdc_path = get_path('rdc_path')
        
        # 检查文件是否存在
        if not os.path.exists(rdc_path):
            print(f"错误: RDC文件不存在: {rdc_path}")
            return False
            
        # 导入RenderDoc文件
        print(f"正在导入RenderDoc文件: {rdc_path}")
        try:
            bpy.ops.import_rdc.google_maps(filepath=(rdc_path), filter_glob=".rdc", max_blocks=-1)
            print("已成功导入RenderDoc文件")
                
        except AttributeError as e:
            print(f"错误: 无法找到RenderDoc导入操作: {str(e)}")
            print("请确保已安装并启用RenderDoc插件")
            return False
        except Exception as e:
            print(f"导入RenderDoc文件时发生错误: {str(e)}")
            return False
            
        # 设置视图
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'area': area, 'region': region}
                        bpy.ops.view3d.view_all(override)
                        print("已调整3D视图")
                        break
        
        # 使用安全的方式设置视图着色模式
        try:
            # 方法1：使用操作符设置着色模式
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    override = {'area': area}
                    bpy.ops.view3d.shading(override, type='MATERIAL')
                    print("已使用操作符切换到Material Preview着色模式")
                    break
        except Exception as e:
            print(f"使用操作符设置着色模式失败: {str(e)}")
            try:
                # 方法2：使用延迟执行的方式
                def set_shading_mode():
                    for area in bpy.context.screen.areas:
                        if area.type == 'VIEW_3D':
                            for space in area.spaces:
                                if space.type == 'VIEW_3D':
                                    space.shading.type = 'MATERIAL'
                                    return True
                    return False
                
                # 注册一个定时器，在UI初始化后执行
                bpy.app.timers.register(set_shading_mode, first_interval=1.0)
                print("已注册定时器来设置Material Preview着色模式")
            except Exception as e2:
                print(f"使用定时器设置着色模式也失败: {str(e2)}")
                print("无法设置着色模式，请在Blender界面中手动设置")
        
        print("Blender内部脚本执行完成")
        return True
        
    except Exception as e:
        print(f"Blender内部脚本执行错误: {str(e)}")
        return False

# 如果直接在Blender中运行此脚本，则执行main函数
if __name__ == "__main__":
    main()