'''
Author: Leili
Date: 2025-04-23 17:46:14
LastEditors: Leili
LastEditTime: 2025-04-24 10:46:03
FilePath: /GoogleModelProcess/mesh_functions.py
Description: 
'''
def remove_distant_vertices(obj_name, threshold_distance):
    """移除距离mesh中心点超过阈值的顶点"""
    import bpy
    
    # 在场景中获取物体
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        raise ValueError(f"未能在场景中找到名为 '{obj_name}' 的物体")
    import bmesh
    import mathutils
    
    # 计算物体的实际几何中心
    sum_co = mathutils.Vector((0, 0, 0))
    for v in obj.data.vertices:
        sum_co += v.co
    center = sum_co / len(obj.data.vertices)
    # 转换到世界空间坐标
    center = obj.matrix_world @ center
    print(f"物体 '{obj_name}' 的几何中心点: {center}")
    
    # 创建bmesh对象
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    
    # 收集需要删除的顶点
    verts_to_remove = []
    for vert in bm.verts:
        # 计算顶点到中心点的距离（需要将顶点坐标转换到世界空间）
        world_vert_co = obj.matrix_world @ vert.co
        distance = (world_vert_co - center).length
        if distance > threshold_distance:
            verts_to_remove.append(vert)
    
    # 删除收集到的顶点
    bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')
    
    # 更新mesh
    bm.to_mesh(obj.data)
    obj.data.update()
    
    # 清理bmesh
    bm.free()

def remove_vertices_below_height(obj_name, height_threshold):
    """移除z坐标低于指定高度的顶点，但保留那些上方有其他顶点的顶点"""

    import bmesh
    # 在场景中获取物体
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        raise ValueError(f"未能在场景中找到名为 '{obj_name}' 的物体")
    
    # 创建bmesh对象
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    
    # 首先标记所有需要检查的顶点
    vertices_below_threshold = set()
    vertices_above_threshold = set()
    
    # 将顶点分类
    for vert in bm.verts:
        world_vert_co = obj.matrix_world @ vert.co
        if world_vert_co.z < height_threshold:
            vertices_below_threshold.add(vert)
        else:
            vertices_above_threshold.add(vert)
    
    # 收集最终需要删除的顶点
    verts_to_remove = set()
    
    # 创建一个字典来存储每个xy位置的顶点
    xy_positions = {}
    
    # 将所有顶点按xy位置分组
    tolerance = 0.01  # xy坐标的容差值
    for vert in bm.verts:
        world_vert_co = obj.matrix_world @ vert.co
        # 将xy坐标四舍五入到指定精度，用作字典键
        xy_key = (round(world_vert_co.x/tolerance)*tolerance, 
                 round(world_vert_co.y/tolerance)*tolerance)
        if xy_key not in xy_positions:
            xy_positions[xy_key] = []
        xy_positions[xy_key].append(vert)
    
    # 检查每个低于阈值的顶点
    for vert in vertices_below_threshold:
        world_vert_co = obj.matrix_world @ vert.co
        xy_key = (round(world_vert_co.x/tolerance)*tolerance, 
                 round(world_vert_co.y/tolerance)*tolerance)
        
        # 检查相同xy位置是否有高于阈值的顶点
        has_upper_vertex = False
        for other_vert in xy_positions[xy_key]:
            other_vert_co = obj.matrix_world @ other_vert.co
            if other_vert in vertices_above_threshold:
                has_upper_vertex = True
                break
        
        # 如果该xy位置没有高于阈值的顶点，则标记为删除
        if not has_upper_vertex:
            verts_to_remove.add(vert)
    
    # 删除收集到的顶点
    if verts_to_remove:
        bmesh.ops.delete(bm, geom=list(verts_to_remove), context='VERTS')
    
    # 更新mesh
    bm.to_mesh(obj.data)
    obj.data.update()
    
    # 清理bmesh
    bm.free()
    
    print(f"已删除 {len(verts_to_remove)} 个低于 {height_threshold} 高度的顶点")

def simplify_meshes(threshold=0.01, ratio=0.5):
    """简化所有网格，保留主要特征"""
    simplified_count = 0
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            # 获取原始顶点数
            original_verts = len(obj.data.vertices)
            
            # 如果顶点数太少，跳过
            if original_verts < 10:
                continue
            
            # 添加解除修改器（如果已存在则跳过）
            decimate_mod = None
            for mod in obj.modifiers:
                if mod.type == 'DECIMATE':
                    decimate_mod = mod
                    break
            
            if not decimate_mod:
                decimate_mod = obj.modifiers.new(name="Decimate", type='DECIMATE')
            
            # 设置解除修改器参数
            decimate_mod.ratio = ratio
            decimate_mod.use_collapse_triangulate = True
            
            # 应用修改器
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=decimate_mod.name)
            
            # 计算简化后的顶点数
            new_verts = len(obj.data.vertices)
            simplified_count += 1
            
            print(f"简化网格: {obj.name}, 顶点数: {original_verts} -> {new_verts}")
    
    return simplified_count


if __name__ == "__main__":
    remove_vertices_below_height("Combined_Mesh", 0.5)
