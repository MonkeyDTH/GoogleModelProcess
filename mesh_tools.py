bl_info = {
    "name": "网格工具",
    "author": "Leili",
    "version": (1, 0, 1),
    "blender": (2, 80, 0),
    "location": "视图3D > 工具栏",
    "description": "网格处理工具集：合并、优化、居中等",
    "category": "Mesh",
}

import bpy
import bmesh
from bpy.types import Operator, Panel
from mathutils import Vector

class MESH_OT_merge_all(Operator):
    """合并场景中所有的网格对象"""
    bl_idname = "mesh.merge_all"
    bl_label = "合并所有网格"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 获取所有网格对象
        mesh_objects = [obj for obj in context.scene.objects if obj.type == 'MESH']
        
        if not mesh_objects:
            self.report({'WARNING'}, "场景中没有网格物体可合并")
            return {'CANCELLED'}
        
        # 确保所有对象都被选中
        bpy.ops.object.select_all(action='DESELECT')
        
        # 选择要合并的对象
        for obj in mesh_objects:
            obj.select_set(True)
        
        # 设置活动对象
        context.view_layer.objects.active = mesh_objects[0]
        
        # 合并对象
        bpy.ops.object.join()
        
        # 重命名合并后的对象
        context.view_layer.objects.active.name = "Combined_Mesh"
        
        self.report({'INFO'}, "网格合并完成")
        return {'FINISHED'}

class MESH_OT_optimize(Operator):
    """优化网格，合并接近的顶点"""
    bl_idname = "mesh.optimize_mesh"
    bl_label = "优化网格"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.active_object or context.active_object.type != 'MESH':
            self.report({'WARNING'}, "请先选择一个网格对象")
            return {'CANCELLED'}
            
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
        
        self.report({'INFO'}, "网格优化完成")
        return {'FINISHED'}

class MESH_OT_center_origin(Operator):
    """将网格XY中心移动到原点，Z轴保持最低点在0"""
    bl_idname = "mesh.center_origin"
    bl_label = "居中到原点"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not context.active_object or context.active_object.type != 'MESH':
            self.report({'WARNING'}, "请先选择一个网格对象")
            return {'CANCELLED'}

        obj = context.active_object
        mesh_data = obj.data
        
        # 计算几何中心和最低点
        vertex_sum = Vector((0, 0, 0))
        min_z = float('inf')
        
        for vertex in mesh_data.vertices:
            world_co = obj.matrix_world @ vertex.co
            vertex_sum += Vector((world_co.x, world_co.y, 0))
            min_z = min(min_z, world_co.z)
        
        vertex_count = len(mesh_data.vertices)
        if vertex_count > 0:
            geometric_center = vertex_sum / vertex_count
            translation_vector = Vector((-geometric_center.x, -geometric_center.y, -min_z))
        else:
            self.report({'WARNING'}, "网格没有顶点")
            return {'CANCELLED'}

        # 应用移动到所有顶点
        for vertex in mesh_data.vertices:
            world_co = obj.matrix_world @ vertex.co
            new_co = world_co + translation_vector
            vertex.co = obj.matrix_world.inverted() @ new_co

        # 更新网格数据
        mesh_data.update()
        obj.location = (0.0, 0.0, 0.0)
        
        self.report({'INFO'}, "网格已居中到原点")
        return {'FINISHED'}

class MESH_OT_remove_unselected(Operator):
    """删除当前网格中所有未被选中的顶点"""
    bl_idname = "mesh.remove_unselected"
    bl_label = "删除未选中顶点"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'WARNING'}, "请先选择一个网格对象")
            return {'CANCELLED'}
        
        # 确保在编辑模式下
        if obj.mode != 'EDIT':
            self.report({'WARNING'}, "请在编辑模式下使用此功能")
            return {'CANCELLED'}
        
        # 创建bmesh对象
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        
        # 收集未选中的顶点
        verts_to_remove = [v for v in bm.verts if not v.select]
        
        if not verts_to_remove:
            self.report({'INFO'}, "没有找到未选中的顶点")
            return {'FINISHED'}
        
        # 删除未选中的顶点
        bmesh.ops.delete(bm, geom=verts_to_remove, context='VERTS')
        
        # 更新网格
        bmesh.update_edit_mesh(obj.data)
        
        self.report({'INFO'}, f"已删除 {len(verts_to_remove)} 个未选中的顶点")
        return {'FINISHED'}

class VIEW3D_PT_mesh_tools(Panel):
    """网格工具面板"""
    bl_label = "网格工具"
    bl_idname = "VIEW3D_PT_mesh_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '工具'

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("mesh.merge_all", text="合并所有网格")
        
        row = layout.row()
        row.operator("mesh.optimize_mesh", text="优化网格")
        
        row = layout.row()
        row.operator("mesh.center_origin", text="居中到原点")
        
        row = layout.row()
        row.operator("mesh.remove_unselected", text="删除未选中顶点")

# 注册
classes = (
    MESH_OT_merge_all,
    MESH_OT_optimize,
    MESH_OT_center_origin,
    MESH_OT_remove_unselected,  # 添加新的类
    VIEW3D_PT_mesh_tools,
)

addon_keymaps = []

def register():
    # 注册类
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # 添加快捷键
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # 合并网格快捷键
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            MESH_OT_merge_all.bl_idname,
            type='M',
            value='PRESS',
            ctrl=True,
            shift=True
        )
        addon_keymaps.append((km, kmi))
        
        # 优化网格快捷键
        kmi = km.keymap_items.new(
            MESH_OT_optimize.bl_idname,
            type='O',
            value='PRESS',
            ctrl=True,
            shift=True
        )
        addon_keymaps.append((km, kmi))
        
        # 居中到原点快捷键
        kmi = km.keymap_items.new(
            MESH_OT_center_origin.bl_idname,
            type='C',
            value='PRESS',
            ctrl=True,
            shift=True
        )
        addon_keymaps.append((km, kmi))
        
        # 删除未选中顶点快捷键
        kmi = km.keymap_items.new(
            MESH_OT_remove_unselected.bl_idname,
            type='D',
            value='PRESS',
            ctrl=True,
            shift=True
        )
        addon_keymaps.append((km, kmi))

def unregister():
    # 移除快捷键
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    # 注销类
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()