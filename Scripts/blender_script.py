'''
Author: Leili
Date: 2025-04-29 16:30:00
LastEditors: Leili
LastEditTime: 2025-05-06 15:50:32
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

# 导入配置工具和日志工具
from Scripts.config_utils import get_path, get_log_level, get_log_dir
from Scripts.log_utils import setup_logger, logD, logI, logW, logE, logEX

# 初始化日志系统
logger = setup_logger(log_level=get_log_level(), log_dir=get_log_dir())

def import_rdc():
    """
    导入RenderDoc文件
    """

    rdc_path = get_path('rdc_path')
    # 检查文件是否存在
    if not os.path.exists(rdc_path):
        logE(f"错误: RDC文件不存在: {rdc_path}")
        return False
        
    # 导入RenderDoc文件
    logI(f"正在导入RenderDoc文件: {rdc_path}")
    try:
        bpy.ops.import_rdc.google_maps(filepath=(rdc_path), filter_glob=".rdc", max_blocks=-1)
        logI("已成功导入RenderDoc文件")
            
    except AttributeError as e:
        logE(f"错误: 无法找到RenderDoc导入操作: {str(e)}")
        logE("请确保已安装并启用RenderDoc插件")
        return False
    except Exception as e:
        logEX(f"导入RenderDoc文件时发生错误: {str(e)}")
        return False

def set_shading_mode():
    """
    使用安全的方式设置视图着色模式
    """
    try:
        # 方法1：直接设置属性
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        try:
                            space.shading.type = 'MATERIAL'
                            logI("已直接设置Material Preview着色模式")
                            break
                        except Exception as e:
                            logW(f"直接设置着色模式失败: {str(e)}")
    except Exception as e:
        logW(f"设置着色模式时发生错误: {str(e)}")
        logW("无法设置着色模式，请在Blender界面中手动设置")

def save_blender_project():
    """
    保存Blender项目
    """
    try:
        # 设置保存目录
        save_dir = get_path("blender_project_dir")
        
        # 检查目录是否存在，如果不存在则创建
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            logI(f"已创建保存目录: {save_dir}")
        
        # 设置自动打包外部资源
        logI("设置自动打包外部资源...")
        # 启用自动打包
        bpy.data.use_autopack = True
        
        # 手动打包所有外部资源
        try:
            # 打包所有外部资源
            bpy.ops.file.pack_all()
            logI("已成功打包所有外部资源")
        except Exception as e:
            logW(f"打包外部资源时发生错误: {str(e)}")
            
        # 确保打包设置在保存时生效
        try:
            # 设置打包选项
            bpy.context.preferences.filepaths.use_file_compression = True
            logI("已启用文件压缩")
        except Exception as e:
            logW(f"设置文件压缩选项时发生错误: {str(e)}")
        
        # 生成当前时间作为文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blend_file_path = os.path.join(save_dir, f"blender_project_{timestamp}.blend")
        
        # 保存Blender项目
        bpy.ops.wm.save_as_mainfile(filepath=blend_file_path, compress=True, relative_remap=True)
        logI(f"已将Blender项目保存至: {blend_file_path}")
        
        # 延迟一小段时间确保文件保存完成
        time.sleep(2)
        
        # 保存完成后自动退出Blender
        logI("保存完成，准备退出Blender...")
        bpy.ops.wm.quit_blender()
        
    except Exception as e:
        logEX(f"保存Blender项目时发生错误: {str(e)}")

def set_viewport_orthographic():
    """
    设置视口为正交投影
    """
    from mathutils import Vector, Quaternion

    # 方法1：使用视图3D区域的视图矩阵
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    # 设置为顶视图（垂直向下看）
                    space.region_3d.view_perspective = 'ORTHO'  # 设置为正交视图
                    space.region_3d.view_rotation = Quaternion((1, 0, 0, 0))  # 顶视图旋转

def count_meshes():
    """
    统计场景中的网格物体数量
    """
    mesh_count = 0
    mesh_objects = []
    vertex_count = 0
    
    # 遍历场景中的所有物体
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mesh_count += 1
            mesh_objects.append(obj.name)
            vertex_count += len(obj.data.vertices)
    
    print(f"场景中共有 {mesh_count} 个网格物体")
    # print(f"网格物体列表: {', '.join(mesh_objects)}")
    print(f"场景中的总顶点数: {vertex_count}")

    return mesh_count, mesh_objects

def merge_all_meshes(merged_name="Combined_Mesh"):
    """
    合并场景中所有的Mesh对象
    """
    # 获取所有网格对象
    mesh_objects = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mesh_objects.append(obj)
    
    if not mesh_objects:
        print("场景中没有网格物体可合并")
        return None
    
    # 统计合并前的网格数量
    print("合并前:")
    initial_count, initial_meshes = count_meshes()
    
    # 确保所有对象都被选中
    bpy.ops.object.select_all(action='DESELECT')
    
    # 选择要合并的对象
    for obj in mesh_objects:
        obj.select_set(True)
    
    # 设置活动对象
    bpy.context.view_layer.objects.active = mesh_objects[0]
    
    # 合并对象
    bpy.ops.object.join()
    
    # 重命名合并后的对象
    bpy.context.view_layer.objects.active.name = merged_name
    
    # 统计合并后的网格数量
    print("\n合并后:")
    final_count, final_meshes = count_meshes()
    
    # 输出统计结果
    print(f"\n合并统计:")
    print(f"初始网格数量: {initial_count}")
    print(f"最终网格数量: {final_count}")
    
    return bpy.context.view_layer.objects.active

def center_mesh_origin(mesh_object=None):
    """
    将指定网格对象的XY中心移动到原点，Z轴保持最低点在0
    """
    from mathutils import Vector
    if mesh_object is None:
        if bpy.context.selected_objects:
            mesh_object = bpy.context.selected_objects[0]
        else:
            print("没有选中任何对象，请先选择一个网格对象")
            return

    if mesh_object.type != 'MESH':
        print(f"选中的对象 '{mesh_object.name}' 不是网格类型")
        return

    print(f"正在将网格 '{mesh_object.name}' 的XY中心移动到原点...")
    # 确保在对象模式下
    bpy.ops.object.mode_set(mode='OBJECT')

    # 计算几何中心和最低点（所有顶点的平均位置）
    mesh_data = mesh_object.data
    vertex_sum = Vector((0, 0, 0))
    min_z = float('inf')
    
    # 计算XY中心和Z轴最低点
    for vertex in mesh_data.vertices:
        # 将顶点坐标从局部空间转换到世界空间
        world_co = mesh_object.matrix_world @ vertex.co
        vertex_sum += Vector((world_co.x, world_co.y, 0))  # 只考虑XY坐标
        min_z = min(min_z, world_co.z)  # 记录最低Z坐标
    
    # 计算平均位置（几何中心）
    vertex_count = len(mesh_data.vertices)
    if vertex_count > 0:
        geometric_center = vertex_sum / vertex_count
        # 只使用XY平移，Z设置为-最低点（这样最低点会在0）
        translation_vector = Vector((-geometric_center.x, -geometric_center.y, -min_z))
    else:
        print("网格没有顶点")
        return

    # 应用移动到所有顶点
    for vertex in mesh_data.vertices:
        # 先转换到世界空间
        world_co = mesh_object.matrix_world @ vertex.co
        # 应用平移
        new_co = world_co + translation_vector
        # 转换回局部空间
        vertex.co = mesh_object.matrix_world.inverted() @ new_co

    # 更新网格数据
    mesh_data.update()

    # 将对象自身的位置重置到原点（因为顶点已经移动了）
    mesh_object.location = (0.0, 0.0, 0.0)

    print(f"网格 '{mesh_object.name}' 已完成居中")

def export_mesh():
    """
    导出当前选中的Mesh为FBX文件
    """
    try:
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建导出目录
        export_dir = os.path.join(project_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # 设置导出文件路径
        export_path = os.path.join(export_dir, f"mesh_export_{timestamp}.fbx")
        
        # 确保选中了要导出的对象
        if not bpy.context.selected_objects:
            print("错误：没有选中任何对象")
            return False
            
        # 设置导出选项
        bpy.ops.export_scene.fbx(
            filepath=export_path,
            use_selection=True,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            bake_space_transform=False,
            object_types={'MESH'},
            use_mesh_modifiers=True,
            mesh_smooth_type='OFF',
            use_mesh_edges=False,
            use_tspace=False,
            use_custom_props=False,
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=False,
            bake_anim=False,
            path_mode='AUTO'
        )
        
        print(f"已将Mesh导出至: {export_path}")
        return True
        
    except Exception as e:
        print(f"导出Mesh时发生错误: {str(e)}")
        return False

def check_export_signal():
    """
    检查是否存在导出信号文件
    """
    signal_file = os.path.join(project_dir, "export_mesh.signal")
    if os.path.exists(signal_file):
        try:
            # 先移除信号文件，防止重复导出
            os.remove(signal_file)
            
            logI("检测到导出信号，开始导出Mesh...")
            if export_mesh():
                # 导出成功后保存Blender项目
                logI("开始保存Blender项目...")
                save_blender_project()
                
                # 创建导出完成信号
                done_file = os.path.join(project_dir, "export_done.signal")
                with open(done_file, 'w') as f:
                    f.write(str(datetime.now()))
                logI("导出和保存完成")
            else:
                logE("导出失败")
                # 如果导出失败，重新创建信号文件以便重试
                with open(signal_file, 'w') as f:
                    f.write(str(datetime.now()))
        except Exception as e:
            logEX(f"处理导出信号时发生错误: {str(e)}")
            # 发生错误时也重新创建信号文件
            try:
                with open(signal_file, 'w') as f:
                    f.write(str(datetime.now()))
            except:
                pass
    return 1.0  # 返回1秒后再次执行

def register_timer():
    """
    注册定时器来检查导出信号
    """
    bpy.app.timers.register(check_export_signal)
    logI("已注册导出信号检查定时器")

def main():
    """
    在Blender内部执行的主函数
    """
    logI("开始执行Blender内部脚本...")
    
    try:
        # 删除场景中的所有物体
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
        logI("已删除场景中的所有物体")
        
        # 导入rdc文件
        ret = import_rdc()

        # 设置视图着色模式
        set_shading_mode()

        # 保存Blender项目
        # save_blender_project()

        # 设置顶视
        set_viewport_orthographic()

        # 合并所有网格
        merged_mesh = merge_all_meshes()
        if merged_mesh:
            print(f"所有网格已成功合并为: {merged_mesh.name}")
            # 合并后居中
            center_mesh_origin(merged_mesh)
        else:
            print("合并操作失败")
        
        logI("Blender内部脚本执行完成")
        
        # 创建信号文件表示脚本执行完成
        signal_file = os.path.join(project_dir, "blender_script_done.signal")
        with open(signal_file, 'w') as f:
            f.write(str(datetime.now()))
            
        # 注册定时器来检查导出信号，而不是使用阻塞的循环
        register_timer()
        
        return True
        
    except Exception as e:
        logEX(f"Blender内部脚本执行错误: {str(e)}")
        return False

# 如果直接在Blender中运行此脚本，则执行main函数
if __name__ == "__main__":
    main()