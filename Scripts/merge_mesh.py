'''
Author: Leili
Date: 2025-04-23
LastEditors: Leili
LastEditTime: 2025-04-28 11:09:31
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

def center_mesh_origin(mesh_object=None):
    """将指定网格对象的XY中心移动到原点，Z轴保持最低点在0"""
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


# 执行合并操作
if __name__ == "__main__":
    merged_mesh = merge_all_meshes()
    if merged_mesh:
        print(f"所有网格已成功合并为: {merged_mesh.name}")
        # 合并后居中
        center_mesh_origin(merged_mesh)
    else:
        print("合并操作失败")

    count_meshes() # 可以取消注释以查看最终统计信息

    # optimize_mesh() # 可以取消注释以进行优化