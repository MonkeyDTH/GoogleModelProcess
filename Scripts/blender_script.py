'''
Author: Leili
Date: 2025-04-29 16:30:00
LastEditors: Leili
LastEditTime: 2025-05-06 13:22:45
FilePath: /GoogleModelProcess/Scripts/blender_script.py
Description: Blender内部操作脚本
'''
import bpy
import os
import sys
import time
from datetime import datetime

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
        
        # 使用安全的方式设置视图着色模式
        try:
            # 方法1：直接设置属性
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            try:
                                space.shading.type = 'MATERIAL'
                                print("已直接设置Material Preview着色模式")
                                break
                            except Exception as e:
                                print(f"直接设置着色模式失败: {str(e)}")
        except Exception as e:
            print(f"设置着色模式时发生错误: {str(e)}")
            print("无法设置着色模式，请在Blender界面中手动设置")
        
        # 保存Blender项目
        try:
            # 设置保存目录
            save_dir = get_path("blender_project_dir")
            
            # 检查目录是否存在，如果不存在则创建
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                print(f"已创建保存目录: {save_dir}")
            
            # 设置自动打包外部资源
            print("设置自动打包外部资源...")
            # 启用自动打包
            bpy.data.use_autopack = True
            
            # 手动打包所有外部资源
            try:
                # 打包所有外部资源
                bpy.ops.file.pack_all()
                print("已成功打包所有外部资源")
            except Exception as e:
                print(f"打包外部资源时发生错误: {str(e)}")
                
            # 确保打包设置在保存时生效
            try:
                # 设置打包选项
                bpy.context.preferences.filepaths.use_file_compression = True
                print("已启用文件压缩")
            except Exception as e:
                print(f"设置文件压缩选项时发生错误: {str(e)}")
            
            # 生成当前时间作为文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blend_file_path = os.path.join(save_dir, f"blender_project_{timestamp}.blend")
            
            # 保存Blender项目
            bpy.ops.wm.save_as_mainfile(filepath=blend_file_path, compress=True, relative_remap=True)
            print(f"已将Blender项目保存至: {blend_file_path}")
            
            # # 延迟一小段时间确保文件保存完成
            # time.sleep(2)
            
            # # 保存完成后自动退出Blender
            # print("保存完成，准备退出Blender...")
            # bpy.ops.wm.quit_blender()
            
        except Exception as e:
            print(f"保存Blender项目时发生错误: {str(e)}")
        
        print("Blender内部脚本执行完成")
        return True
        
    except Exception as e:
        print(f"Blender内部脚本执行错误: {str(e)}")
        return False

# 如果直接在Blender中运行此脚本，则执行main函数
if __name__ == "__main__":
    main()