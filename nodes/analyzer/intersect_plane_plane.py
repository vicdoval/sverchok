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
from bpy.props import FloatProperty, FloatVectorProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, match_long_repeat
from mathutils import Vector as V
from mathutils.geometry import intersect_line_sphere, distance_point_to_plane, intersect_plane_plane, normal, barycentric_transform


def compute_intersect_plane_plane(params, result, gates):

    plane_co_a, plane_norm_a, plane_co_b, plane_norm_b = params
    
    local_result = []
    plane_co_a_V = V(plane_co_a)
    plane_norm_a_V = V(plane_norm_a)
    plane_co_b_V = V(plane_co_b)
    plane_norm_b_V = V(plane_norm_b)

    inter_p = intersect_plane_plane(plane_co_a_V, plane_norm_a_V, plane_co_b_V, plane_norm_b_V)

    if inter_p[0]:
        intersect = True
        line_origin = list(inter_p[1])
        line_direction = list(inter_p[0])
    else:
        print("Error:  Planes are parallel")
        intersect = False
        line_origin = list(plane_co_a_V)
        line_direction = list(plane_norm_a_V)
        
    local_result =[intersect, line_origin, line_direction]

    for i, r in enumerate(result):
        if gates[i]:
            r.append(local_result[i])


class SvIntersectPlanePlaneNode(bpy.types.Node, SverchCustomTreeNode):
    '''
    Triggers: Line from Plane Intersection
    Tooltip: Intersect two planes and get the resulting line.
    '''
    bl_idname = 'SvIntersectPlanePlaneNode'
    bl_label = 'Plane Intersection'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_DISTANCE'

    plane_loc_a = FloatVectorProperty(
        name="Location A", description='First Plane point',
        size=3, default=(0, 0, 0),
        update=updateNode)

    plane_normal_a = FloatVectorProperty(
        name='Normal A', description='First Plane Normal',
        size=3, default=(0, 0, 1),
        update=updateNode)

    plane_loc_b = FloatVectorProperty(
        name="Location B", description='Second Plane point',
        size=3, default=(0, 0, 0),
        update=updateNode)

    plane_normal_b = FloatVectorProperty(
        name='Normal B', description='Second Plane Normal',
        size=3, default=(0, 1, 0),
        update=updateNode)


    def sv_init(self, context):
        '''create sockets'''
        sinw = self.inputs.new
        sonw = self.outputs.new
        sinw('VerticesSocket', 'Location A').prop_name = 'plane_loc_a'
        sinw('VerticesSocket', 'Normal A').prop_name = 'plane_normal_a'
        sinw('VerticesSocket', 'Location B').prop_name = 'plane_loc_b'
        sinw('VerticesSocket', 'Normal B').prop_name = 'plane_normal_b'

        sonw('StringsSocket', 'Intersect')
        sonw('VerticesSocket', 'Origin')
        sonw('VerticesSocket', 'Direction')


    def get_data(self):
        '''get all data from sockets'''
        si = self.inputs
        plane_co_a = si['Location A'].sv_get(default=[[]])
        plane_norm_a = si['Normal A'].sv_get(default=[[]])
        plane_co_b = si['Location B'].sv_get(default=[[]])
        plane_norm_b = si['Normal B'].sv_get(default=[[]])

        return match_long_repeat([plane_co_a, plane_norm_a, plane_co_b, plane_norm_b])

    def process(self):
        '''main node function called every update'''
        so = self.outputs
        si = self.inputs
        if not (any(s.is_linked for s in so)):
            return

        result = [[], [], []]
        gates = []
        gates.append(so['Intersect'].is_linked)
        gates.append(so['Origin'].is_linked)
        gates.append(so['Direction'].is_linked)

        group = self.get_data()

        for subgroup in zip(*group):
            subgroup = match_long_repeat(subgroup)
            subresult = [[], [], []]
            for p in zip(*subgroup):
                compute_intersect_plane_plane(p, subresult, gates)
            for i, r in enumerate(result):
                if gates[i]:
                    r.append(subresult[i])

        for i, r in enumerate(result):
            if gates[i]:
                so[i].sv_set(result[i])


def register():
    '''register class in Blender'''
    bpy.utils.register_class(SvIntersectPlanePlaneNode)


def unregister():
    '''unregister class in Blender'''
    bpy.utils.unregister_class(SvIntersectPlanePlaneNode)
