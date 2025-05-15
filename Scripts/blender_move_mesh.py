'''
Author: Leili
Date: 2025-05-14 17:58:39
LastEditors: Leili
LastEditTime: 2025-05-15 11:51:06
FilePath: /GoogleModelProcess/Scripts/blender_move_mesh.py
Description: 
'''
import bpy
import mathutils


def set_mesh_transform(mesh_name, location=None, rotation_euler=None, scale=None):
    """
    修改指定网格对象的变换属性。

    参数:
    mesh_name (str): 要修改的网格对象的名称。
    location (tuple or mathutils.Vector): 新的位置 (x, y, z)。如果为 None，则不修改位置。
    rotation_euler (tuple or mathutils.Euler): 新的欧拉旋转 (x, y, z)，单位为弧度。如果为 None，则不修改旋转。
    scale (tuple or mathutils.Vector): 新的缩放 (x, y, z)。如果为 None，则不修改缩放。
    """
    # 获取场景中的对象
    obj = bpy.data.objects.get(mesh_name)

    if obj is None:
        print(f"错误：找不到名为 '{mesh_name}' 的对象。")
        return False

    if obj.type != 'MESH':
        print(f"错误：对象 '{mesh_name}' 不是一个网格对象，其类型为 '{obj.type}'。")
        return False

    print(f"正在修改对象 '{mesh_name}' 的变换属性...")

    # 修改位置
    if location is not None:
        if len(location) == 3:
            obj.location = mathutils.Vector(location)
            print(f"  位置已设置为: {obj.location}")
        else:
            print(f"  警告：提供的location参数 '{location}' 无效，应为包含3个元素的元组或向量。")

    # 修改旋转 (欧拉角)
    if rotation_euler is not None:
        if len(rotation_euler) == 3:
            obj.rotation_mode = 'XYZ'  # 确保旋转模式为欧拉角
            obj.rotation_euler = mathutils.Euler(rotation_euler, 'XYZ')
            print(f"  欧拉旋转已设置为: {obj.rotation_euler}")
        else:
            print(f"  警告：提供的rotation_euler参数 '{rotation_euler}' 无效，应为包含3个元素的元组或向量。")

    # 修改缩放
    if scale is not None:
        if len(scale) == 3:
            obj.scale = mathutils.Vector(scale)
            print(f"  缩放已设置为: {obj.scale}")
        else:
            print(f"  警告：提供的scale参数 '{scale}' 无效，应为包含3个元素的元组或向量。")

    print(f"对象 '{mesh_name}' 的变换属性修改完成。")
    return True


# 示例用法 (在Blender脚本编辑器中运行时取消注释并修改参数)
if __name__ == "__main__":
    # 请确保场景中有一个名为 "Cube" 的网格对象
    # 如果没有，请创建一个立方体并将其命名为 "Cube"
    # 或者将 "Cube" 替换为您场景中实际的网格对象名称

    mesh_to_modify = "Mesh1"  # 替换为你的网格对象名称

    # 检查对象是否存在
    if mesh_to_modify not in bpy.data.objects:
        print(f"示例错误：场景中不存在名为 '{mesh_to_modify}' 的对象。请创建它或修改脚本中的名称。")
    else:
        # 设置新的变换值
        new_location = (1.0, 2.0, 3.0)
        new_rotation = (0.0, 0.0, 1.5708)  # 绕Z轴旋转90度 (pi/2)
        new_scale = (1.5, 1.5, 0.5)

        success = set_mesh_transform(mesh_to_modify, 
                                     location=new_location, 
                                     rotation_euler=new_rotation, 
                                     scale=new_scale)

        if success:
            print(f"成功修改 '{mesh_to_modify}' 的变换。")
        else:
            print(f"修改 '{mesh_to_modify}' 的变换失败。")

        # 只修改位置
        # set_mesh_transform(mesh_to_modify, location=(5,5,5))

        # 只修改旋转
        # set_mesh_transform(mesh_to_modify, rotation_euler=(0.7854, 0, 0)) # 绕X轴旋转45度

        # 只修改缩放
        # set_mesh_transform(mesh_to_modify, scale=(2,2,2))