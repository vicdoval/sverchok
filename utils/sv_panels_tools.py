# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import webbrowser

import bpy
from bpy.props import StringProperty, CollectionProperty, BoolProperty

from sverchok.core.update_system import process_tree, build_update_list
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.utils.logging import debug, info
import sverchok


class SverchokUpdateAll(bpy.types.Operator):
    """Sverchok update all"""
    bl_idname = "node.sverchok_update_all"
    bl_label = "Sverchok update all"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sv_ngs = filter(lambda ng:ng.bl_idname == 'SverchCustomTreeType', bpy.data.node_groups)
        for ng in sv_ngs:
            ng.unfreeze(hard=True)
        build_update_list()
        process_tree()
        return {'FINISHED'}


class SverchokBakeAll(bpy.types.Operator):
    """Bake all nodes on this layout"""
    bl_idname = "node.sverchok_bake_all"
    bl_label = "Sverchok bake all"
    bl_options = {'REGISTER', 'UNDO'}

    node_tree_name: StringProperty(name='tree_name', default='')

    @classmethod
    def poll(cls, context):
        if bpy.data.node_groups.__len__():
            return True
        else:
            return False

    def execute(self, context):
        ng = bpy.data.node_groups[self.node_tree_name]
        nodes = filter(lambda n: hasattr(n, "bake"), ng.nodes)
        for node in nodes:
            if node.bakebuttonshow:
                node.bake()

        return {'FINISHED'}


class SverchokUpdateCurrent(bpy.types.Operator):
    """Sverchok update all"""
    bl_idname = "node.sverchok_update_current"
    bl_label = "Sverchok update all"
    bl_options = {'REGISTER', 'UNDO'}

    node_group: StringProperty(default="")

    def execute(self, context):
        ng = bpy.data.node_groups.get(self.node_group)
        if ng:
            ng.unfreeze(hard=True)
            build_update_list(ng)
            process_tree(ng)
        return {'FINISHED'}


class SverchokPurgeCache(bpy.types.Operator):
    """Sverchok purge cache"""
    bl_idname = "node.sverchok_purge_cache"
    bl_label = "Sverchok purge cache"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        info(bpy.context.space_data.node_tree.name)
        return {'FINISHED'}


# USED IN CTRL+U PROPERTIES WINDOW
class SverchokHome(bpy.types.Operator):
    """Sverchok Home"""
    bl_idname = "node.sverchok_home"
    bl_label = "Sverchok go home"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        page = 'http://nikitron.cc.ua/blend_scripts.html'
        if context.scene.use_webbrowser:
            try:
                webbrowser.open_new_tab(page)
            except:
                self.report({'WARNING'}, "Error in opening the page %s." % (page))
        return {'FINISHED'}



class SvSwitchToLayout (bpy.types.Operator):
    """Switch to exact layout, user friendly way"""
    bl_idname = "node.sv_switch_layout"
    bl_label = "switch layouts"
    bl_options = {'REGISTER', 'UNDO'}

    layout_name: bpy.props.StringProperty(
        default='', name='layout_name',
        description='layout name to change layout by button')

    @classmethod
    def poll(cls, context):
        if context.space_data.type == 'NODE_EDITOR':
            if bpy.context.space_data.tree_type == 'SverchCustomTreeType':
                return True
        else:
            return False

    def execute(self, context):
        ng = bpy.data.node_groups.get(self.layout_name)
        if ng and context.space_data.edit_tree.name != self.layout_name:
            context.space_data.path.start(bpy.data.node_groups[self.layout_name])
        else:
            return {'CANCELLED'}
        return {'FINISHED'}




class SvClearNodesLayouts (bpy.types.Operator):
    """Clear node layouts sverchok and blendgraph, when no nodes editor opened"""
    bl_idname = "node.sv_delete_nodelayouts"
    bl_label = "del layouts"
    bl_options = {'REGISTER', 'UNDO'}

    do_clear: bpy.props.BoolProperty(
        default=False, name='even used',
        description='remove even if layout has one user (not fake user)')

    @classmethod
    def poll(cls, self):
        for area in bpy.context.window.screen.areas:
            if area.type == 'NODE_EDITOR':
                return False
        return True

    def execute(self, context):
        trees = bpy.data.node_groups
        for T in trees:
            if T.bl_rna.name in ['Shader Node Tree']:
                continue
            if trees[T.name].users > 1 and T.use_fake_user:
                info('Layout '+str(T.name)+' protected by fake user.')
            if trees[T.name].users >= 1 and self.do_clear and not T.use_fake_user:
                info('cleaning user: '+str(T.name))
                trees[T.name].user_clear()
            if trees[T.name].users == 0:
                info('removing layout: '+str(T.name)+' | '+str(T.bl_rna.name))
                bpy.data.node_groups.remove(T)

        return {'FINISHED'}


class Sv3dPropItem(bpy.types.PropertyGroup):
    node_name: StringProperty()


class Sv3dPropRemoveItem(bpy.types.Operator):
    ''' remove item by node_name from tree.Sv3Dprops  '''

    bl_idname = "node.sv_remove_3dviewpropitem"
    bl_label = "remove item from Sv3Dprops - useful for removed nodes"

    tree_name: StringProperty(description="store tree name")
    node_name: StringProperty(description="store node name")

    def execute(self, context):

        tree = bpy.data.node_groups[self.tree_name]
        props = tree.Sv3DProps

        for index in range(len(props)):
            if props[index].node_name == self.node_name:
                props.remove(index)
                return {'FINISHED'}

        return {'CANCELLED'}




class SvLayoutScanProperties(bpy.types.Operator):
    ''' scan layouts of sverchok for properties '''

    bl_idname = "node.sv_scan_propertyes"
    bl_label = "scan for propertyes in sverchok leyouts"

    def execute(self, context):
        for tree in bpy.data.node_groups:

            if not tree.bl_idname == 'SverchCustomTreeType':
                continue

            node_names = []
            for node in tree.nodes:
                if hasattr(node, 'draw_3dpanel'):
                    if node.draw_3dpanel:
                        node_names.append(node.name)
                    else:
                        debug(f"Node {node.name} could be drawn on N panel but 'draw_3dpanel' have returned False")

            node_names.sort()
            tree.Sv3DProps.clear()
            for name in node_names:
                debug(f'sverchok 3d panel appended with {name}')
                item = tree.Sv3DProps.add()
                item.node_name = name

        return {'FINISHED'}

def bake_animation_to_shapekeys(context, data):
    '''Moves along animation range duplicating the updated object and merging it with a new object as a shapekey'''
    original_name = context.active_object.name
    first_frame = context.scene.frame_start
    end_frame = context.scene.frame_end
    context.scene.frame_current = first_frame
    bpy.ops.node.sverchok_update_all()
    bpy.ops.object.duplicate()
    context.active_object.name = 'Baked_' + original_name
    context.active_object.data.name = 'Baked_' + original_name
    data.objects[original_name].select_set(state=True)
    bpy.ops.object.join_shapes()
    for actual_frame in range(first_frame + 1, end_frame + 1):
        print("Baking "+ original_name + ", frame number:" +  str(actual_frame))
        context.scene.frame_current = actual_frame
        bpy.ops.node.sverchok_update_all()
        bpy.ops.object.join_shapes()
        context.object.active_shape_key_index = actual_frame - 1
        keys_name = context.object.data.shape_keys.name
        object_shape_keys = data.shape_keys[keys_name]
        object_shape_keys.key_blocks[-1].value = 1
        name = data.shape_keys[keys_name].key_blocks[-1].name
        shapekey_data_path = 'key_blocks["'+ name +'"].value'
        data.shape_keys[keys_name].keyframe_insert(data_path=shapekey_data_path)
        object_shape_keys.key_blocks[-2].value = 0
        name_p = data.shape_keys[keys_name].key_blocks[-2].name
        shapekey_data_path_p = 'key_blocks["'+ name_p +'"].value'
        data.shape_keys[keys_name].keyframe_insert(data_path=shapekey_data_path_p)
        context.scene.frame_current = actual_frame - 1
        object_shape_keys.key_blocks[-1].value = 0
        data.shape_keys[keys_name].keyframe_insert(data_path=shapekey_data_path)

class SvBakeAnimationToShapekeys(bpy.types.Operator):
    """Bake active object animation to new object with shapekeys"""
    bl_idname = "object.bake_animation_to_shapekeys"
    bl_label = "Bake Sverchok Animation to Shapekeys"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        data = bpy.data
        bake_animation_to_shapekeys(context, data)
        return {'FINISHED'}

sv_tools_classes = [
    SverchokUpdateCurrent,
    SverchokUpdateAll,
    SverchokBakeAll,
    SverchokPurgeCache,
    SverchokHome,
    Sv3dPropItem,
    Sv3dPropRemoveItem,
    SvSwitchToLayout,
    SvLayoutScanProperties,
    SvClearNodesLayouts,
    SvBakeAnimationToShapekeys
]


def register():
    bpy.types.Scene.sv_do_clear = bpy.props.BoolProperty(
        default=False, name='even used', description='remove even if \
        layout has one user (not fake user)')

    for class_name in sv_tools_classes:
        bpy.utils.register_class(class_name)

    bpy.types.NodeTree.Sv3DProps = CollectionProperty(type=Sv3dPropItem)
    bpy.types.Scene.sv_new_version = BoolProperty(default=False)


def unregister():
    # cargo cult to unregister in reverse order? I don't think this is needed.
    # maybe it was handy at some point?
    del bpy.types.NodeTree.Sv3DProps

    for class_name in reversed(sv_tools_classes):
        bpy.utils.unregister_class(class_name)
