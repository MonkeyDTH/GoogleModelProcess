'''
Author: Leili
Date: 2025-04-24 16:43:42
LastEditors: Leili
LastEditTime: 2025-04-27 16:17:32
FilePath: /GoogleModelProcess/render.py
Description: 
'''
import bpy
import math
from mathutils import Vector
import time

def setup_camera_animation(target_obj_name, frames=250, radius=5.0, height=2.0):
    """设置相机环绕动画
    
    Args:
        target_obj_name: 目标物体名称
        frames: 总帧数
        radius: 相机环绕半径
        height: 相机高度
    """
    # 获取目标物体
    target = bpy.data.objects.get(target_obj_name)
    if not target:
        raise ValueError(f"未找到目标物体: {target_obj_name}")
    
    # 计算物体的几何中心
    sum_co = Vector((0, 0, 0))
    for v in target.data.vertices:
        sum_co += v.co
    center = sum_co / len(target.data.vertices)
    # 转换到世界空间坐标
    center = target.matrix_world @ center
    print(f"物体 '{target_obj_name}' 的几何中心点: {center}")
    
    # 创建相机（如果不存在）
    camera = bpy.data.objects.get('Camera')
    if not camera:
        bpy.ops.object.camera_add()
        camera = bpy.data.objects['Camera']
    
    # 设置相机位置和朝向
    camera.location = Vector((radius, 0, height))
    
    # 创建空物体作为相机的目标点
    target_empty = bpy.data.objects.get('CameraTarget')
    if not target_empty:
        bpy.ops.object.empty_add(type='PLAIN_AXES')
        target_empty = bpy.data.objects['Empty']
        target_empty.name = 'CameraTarget'
    
    # 将目标点放在物体的几何中心
    target_empty.location = center
    
    # 添加跟踪约束，使相机始终朝向目标
    track_to = camera.constraints.new(type='TRACK_TO')
    track_to.target = target_empty
    track_to.track_axis = 'TRACK_NEGATIVE_Z'
    track_to.up_axis = 'UP_Y'
    
    # 设置场景帧范围
    scene = bpy.context.scene
    scene.frame_start = 0
    scene.frame_end = frames
    
    # 创建相机动画
    for frame in range(frames + 1):
        # 计算当前角度
        angle = (frame / frames) * 2 * math.pi
        
        # 计算相机位置
        x = center.x + radius * math.cos(angle)
        y = center.y + radius * math.sin(angle)
        z = height
        
        # 设置相机位置
        camera.location = Vector((x, y, z))
        
        # 插入关键帧
        camera.keyframe_insert(data_path="location", frame=frame)
    
    # 设置当前相机为活动相机
    scene.camera = camera
    
    # 添加光照
    # 1. 主光源 - 太阳光
    sun = bpy.data.lights.get('Sun')
    if not sun:
        sun = bpy.data.lights.new(name='Sun', type='SUN')
    sun_obj = bpy.data.objects.get('Sun')
    if not sun_obj:
        sun_obj = bpy.data.objects.new(name='Sun', object_data=sun)
        bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.location = Vector((15, 15, 20))
    sun_obj.rotation_euler = (math.radians(45), math.radians(45), 0)
    sun.energy = 5.0  # 调整光照强度
    
    # 2. 环境光
    if not bpy.context.scene.world:
        bpy.context.scene.world = bpy.data.worlds.new("World")
    bpy.context.scene.world.use_nodes = True
    world_nodes = bpy.context.scene.world.node_tree.nodes
    world_nodes["Background"].inputs[1].default_value = 1.0  # 调整环境光强度
    
    # 3. 补光 - 添加一个区域光源
    area = bpy.data.lights.get('Area')
    if not area:
        area = bpy.data.lights.new(name='Area', type='AREA')
    area_obj = bpy.data.objects.get('Area')
    if not area_obj:
        area_obj = bpy.data.objects.new(name='Area', object_data=area)
        bpy.context.scene.collection.objects.link(area_obj)
    area_obj.location = Vector((-10, -10, 10))
    area_obj.rotation_euler = (math.radians(-45), math.radians(-45), 0)
    area.energy = 300.0  # 区域光强度
    area.size = 5.0  # 光源大小

def render_animation(output_path, resolution_x=1920, resolution_y=1080, fps=60):
    """渲染动画
    
    Args:
        output_path: 输出路径
        resolution_x: 分辨率宽度
        resolution_y: 分辨率高度
        fps: 帧率
    """
    scene = bpy.context.scene
    
    # 设置渲染参数
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.fps = fps
    
    # 设置输出路径
    scene.render.filepath = output_path
    
    # 开始渲染
    bpy.ops.render.render(animation=True)

if __name__ == "__main__":

    start = time.time()
    # 设置相机动画
    setup_camera_animation("inglewood 填充", frames=1200, radius=18.0, height=12.0)
    
    # 渲染动画
    render_animation("D:/Projects/X/GoogleModelProcess/Render/20250425.mp4")
    time_spent = time.time() - start
    print(f"渲染完成，耗时 {time_spent:.2f} 秒")
