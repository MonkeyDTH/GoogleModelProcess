'''
Author: Leili
Date: 2025-04-23
LastEditors: Leili
LastEditTime: 2025-04-23 19:01:34
FilePath: /GoogleModelProcess/merge_mesh.py
Description: 合并场景中所有的Mesh对象
'''
import bpy
from mathutils import Vector

def count_meshes():
    """统计场景中的网格物体数量"""
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
    """合并场景中所有的Mesh对象"""
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


def optimize_mesh(mesh_object=None):
    """ 优化网格, 合并接近的顶点 """
    if mesh_object is None:
        if bpy.context.selected_objects:
            mesh_object = bpy.context.selected_objects[0]
        else:
            print("没有选中任何对象，请先选择一个网格对象")
            return []

    if mesh_object.type != 'MESH':
        print(f"选中的对象 '{mesh_object.name}' 不是网格类型")
        return []

    print("正在优化网格数据...")
    # 确保在对象模式下
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 移除重复顶点
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    
    # 合并接近的顶点
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.vert_connect_nonplanar(angle_limit=0.001)
    
    # 更新网格数据
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh_data = mesh_object.data
    print(f"优化后顶点数: {len(mesh_data.vertices)}")


# 执行合并操作
if __name__ == "__main__":
    merged_mesh = merge_all_meshes()
    if merged_mesh:
        print(f"所有网格已成功合并为: {merged_mesh.name}")
    else:
        print("合并操作失败")

    count_meshes()

    # 询问用户是否要分割网格
    # split_objects = split_combined_mesh()
    # if split_objects:
    #     print(f"网格已成功分割为 {len(split_objects)} 个独立实体")
    # else:
    #     print("分割操作失败")
    
    # optimize_mesh()