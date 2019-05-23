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
from mathutils.geometry import intersect_line_sphere, intersect_point_line, intersect_sphere_sphere_2d, normal, barycentric_transform


def compute_intersect_circle_circle(params, result, gates):

    v_in_plane, center_a, radius_a, center_b, radius_b = params
    local_result = []
    sphere_loc_a = V(center_a)
    sphere_loc_b = V(center_b)
    v_in_plane_V = V(v_in_plane)
    norm = normal([sphere_loc_a, sphere_loc_b, v_in_plane_V])
    if norm.length == 0:
        print("Error: the point in plane is aligned with origins")
    is_2d = norm.x == 0 and norm.y == 0

    if is_2d:
        z_coord = sphere_loc_a.z
        inter_p = intersect_sphere_sphere_2d(sphere_loc_a.to_2d(), radius_a, sphere_loc_b.to_2d(), radius_b)
        if inter_p[0]:
            intersect = True
            v1 = list(inter_p[1]) + [z_coord]
            v0 = list(inter_p[0]) + [z_coord]
            local_result =[intersect, v0, v1]

    else:
        dist = (sphere_loc_a - sphere_loc_b).length
        new_a = V([0,0,0])
        new_b = V([dist,0,0])
        inter_p = intersect_sphere_sphere_2d(new_a.to_2d(), radius_a, new_b.to_2d(), radius_b)
        if inter_p[0]:
            intersect_num = True
            v0 = barycentric_transform(inter_p[0].to_3d(), new_a, new_b, V([0, 0, 1]), sphere_loc_a, sphere_loc_b, norm)
            v1 = barycentric_transform(inter_p[1].to_3d(), new_a, new_b, V([0, 0, 1]), sphere_loc_a, sphere_loc_b, norm)
            local_result =[intersect_num, list(v0), list(v1)]

    if not local_result:
        dir = (sphere_loc_b - sphere_loc_a).normalized()
        intersect_num = False
        v0 = sphere_loc_a + dir * radius_a
        v1 = sphere_loc_b - dir * radius_b
        local_result = [intersect_num, list(v0), list(v1)]

    for i, r in enumerate(result):
        if gates[i]:
            r.append(local_result[i])


class SvIntersectCircleCircleNode(bpy.types.Node, SverchCustomTreeNode):
    '''
    Triggers: Intersect Circle Circle
    Tooltip: Intersect between to co-planar Circles.
    '''
    bl_idname = 'SvIntersectCircleCircleNode'
    bl_label = 'Circle Intersection'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_DISTANCE'

    radius_A = FloatProperty(
        name="Radius", description='intersection tolerance',
        default=1, min=0.0,
        update=updateNode)

    sphere_center_A = FloatVectorProperty(
        name='Center', description='Origin of sphere',
        size=3, default=(0, 0, 0),
        update=updateNode)

    radius_B = FloatProperty(
        name="Radius", description='intersection tolerance',
        default=1, min=0.0,
        update=updateNode)

    sphere_center_B = FloatVectorProperty(
        name='Center', description='Origin of sphere',
        size=3, default=(0, 0, 0),
        update=updateNode)

    v_in_plane = FloatVectorProperty(
        name='Pt. in plane', description='Origin of sphere',
        size=3, default=(0, 0, 0),
        update=updateNode)

    def sv_init(self, context):
        '''create sockets'''
        sinw = self.inputs.new
        sonw = self.outputs.new
        sinw('VerticesSocket', 'Center A').prop_name = 'sphere_center_A'
        sinw('StringsSocket', 'Radius A').prop_name = 'radius_A'
        sinw('VerticesSocket', 'Center B').prop_name = 'sphere_center_B'
        sinw('StringsSocket', 'Radius B').prop_name = 'radius_B'
        sinw('VerticesSocket', 'Pt. in plane').prop_name = 'v_in_plane'

        sonw('StringsSocket', 'Intersect Num')
        sonw('VerticesSocket', 'Intersection A')
        sonw('VerticesSocket', 'Intersection B')


    def get_data(self):
        '''get all data from sockets'''
        si = self.inputs
        center_a = si['Center A'].sv_get(default=[[]])
        radius_a = si['Radius A'].sv_get(default=[[]])
        center_b = si['Center B'].sv_get(default=[[]])
        radius_b = si['Radius B'].sv_get(default=[[]])
        v_in_plane = si['Pt. in plane'].sv_get(default=[[]])

        return match_long_repeat([v_in_plane, center_a, radius_a, center_b, radius_b])

    def process(self):
        '''main node function called every update'''
        so = self.outputs
        si = self.inputs
        if not (any(s.is_linked for s in so)):
            return

        result = [[], [], []]
        gates = []
        gates.append(so['Intersect Num'].is_linked)
        gates.append(so['Intersection A'].is_linked)
        gates.append(so['Intersection B'].is_linked)

        group = self.get_data()

        for vs_in_plane, center_as, radius_as, center_bs, radius_bs in zip(*group):
            subgroup = match_long_repeat([vs_in_plane, center_as, radius_as, center_bs, radius_bs ])
            subresult = [[], [], []]
            for p in zip(*subgroup):
                compute_intersect_circle_circle(p, subresult, gates)
            for i, r in enumerate(result):
                if gates[i]:
                    r.append(subresult[i])

        for i, r in enumerate(result):
            if gates[i]:
                so[i].sv_set(result[i])


def register():
    '''register class in Blender'''
    bpy.utils.register_class(SvIntersectCircleCircleNode)


def unregister():
    '''unregister class in Blender'''
    bpy.utils.unregister_class(SvIntersectCircleCircleNode)
