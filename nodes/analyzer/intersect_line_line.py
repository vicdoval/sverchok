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


import bpy
from bpy.props import FloatProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, match_long_repeat
from mathutils import Vector as V
from mathutils.geometry import intersect_line_line, intersect_point_line


def compute_intersect_line_line(line_a, line_b, result, gates, tolerance):
    '''pass the data to the mathutils function'''
    line_origin_a = V(line_a[0])
    line_end_a = V(line_a[-1])
    line_origin_b = V(line_b[0])
    line_end_b = V(line_b[-1])

    inter_p = intersect_line_line(line_origin_a, line_end_a, line_origin_b, line_end_b)

    if inter_p:
        dist = (inter_p[0] - inter_p[1]).length
        is_in_line = dist < tolerance

        local_result = [dist, is_in_line, list(inter_p[1]), list(inter_p[0])]
    else:
        inter_p = intersect_point_line(line_origin_a, line_origin_b, line_end_b)
        dist = (inter_p[0] - line_origin_b).length
        is_in_line = dist < tolerance
        local_result = [dist, is_in_line, line_a[0], list(inter_p[0])]


    for i, r in enumerate(result):
        if gates[i]:
            r.append([local_result[i]])


class SvIntersectLineLineNode(bpy.types.Node, SverchCustomTreeNode):
    '''
    Triggers: Distance, Trim
    Tooltip: Distance Line to line and closest points in the lines
    '''
    bl_idname = 'SvIntersectLineLineNode'
    bl_label = 'Line Intersection'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_DISTANCE'

    tolerance = FloatProperty(
        name="tolerance", description='intersection tolerance',
        default=1.0e-6, min=0.0, precision=6,
        update=updateNode)

    def sv_init(self, context):
        '''create sockets'''
        sinw = self.inputs.new
        sonw = self.outputs.new
        sinw('VerticesSocket', "Verts Line A")
        sinw('VerticesSocket', "Verts Line B")

        sonw('StringsSocket', "Distance")
        sonw('StringsSocket', "Intersect")
        sonw('VerticesSocket', "Closest Point A")
        sonw('VerticesSocket', "Closest Point B")

    def draw_buttons_ext(self, context, layout):
        '''draw buttons on the N-panel'''
        layout.prop(self, "tolerance")

    def get_data(self):
        '''get all data from sockets'''
        si = self.inputs
        verts_line_a = si['Verts Line A'].sv_get(default=[[]])
        verts_line_b = si['Verts Line B'].sv_get(default=[[]])

        return match_long_repeat([verts_line_a, verts_line_b])

    def process(self):
        '''main node function called every update'''
        so = self.outputs
        si = self.inputs
        if not (any(s.is_linked for s in so) and all(s.is_linked for s in si)):
            return

        result = [[], [], [], []]
        gates = []
        gates.append(so['Distance'].is_linked)
        gates.append(so['Intersect'].is_linked)
        gates.append(so['Closest Point A'].is_linked)
        gates.append(so['Closest Point B'].is_linked)

        group = self.get_data()

        for line_a, line_b in zip(*group):
            compute_intersect_line_line(line_a, line_b, result, gates, self.tolerance)

        for i, r in enumerate(result):
            if gates[i]:
                so[i].sv_set(result[i])


def register():
    '''register class in Blender'''
    bpy.utils.register_class(SvIntersectLineLineNode)


def unregister():
    '''unregister class in Blender'''
    bpy.utils.unregister_class(SvIntersectLineLineNode)
