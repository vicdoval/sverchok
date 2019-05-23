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
from mathutils.geometry import intersect_line_sphere, intersect_point_line


def compute_intersect_line_sphere(line, sphere_loc, sphere_r, result, gates, tolerance):
    '''pass the data to the mathutils function'''
    line_origin = V(line[0])
    line_end = V(line[-1])
    sphere_v = V(sphere_loc)
    inter_p = intersect_line_sphere(line_origin, line_end, sphere_v, sphere_r)

    if inter_p[0] or inter_p[1]:
        if not inter_p[0]:
            inter_p = (inter_p[1], inter_p[0])        
        if inter_p[1]:
            intersect_num = 2
            v1 = list(inter_p[1])
        else:
            intersect_num = 1
            v1 = list(inter_p[0])  
               
        v0 = list(inter_p[0]) 
       
        local_result = [intersect_num, v0, v1]
    else:
        inter_p = intersect_point_line(sphere_v, line_origin, line_end)
        dir = (inter_p[0] - sphere_v).normalized() * sphere_r
        intersect_num = 0
        local_result = [intersect_num, list(sphere_v + dir), list(inter_p[0])]


    for i, r in enumerate(result):
        if gates[i]:
            r.append(local_result[i])


class SvIntersectLineSphereNode(bpy.types.Node, SverchCustomTreeNode):
    '''
    Triggers: Intersect Line Sphere
    Tooltip: Distance Line to line and closest points in the lines
    '''
    bl_idname = 'SvIntersectLineSphereNode'
    bl_label = 'Compass 3D'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_DISTANCE'

    tolerance = FloatProperty(
        name="tolerance", description='intersection tolerance',
        default=1.0e-6, min=0.0, precision=6,
        update=updateNode)
        
    radius = FloatProperty(
        name="Radius", description='intersection tolerance',
        default=1, min=0.0,
        update=updateNode)

    sphere_center = FloatVectorProperty(
        name='Center', description='Origin of sphere',
        size=3, default=(0, 0, 0),
        update=updateNode)

    def sv_init(self, context):
        '''create sockets'''
        sinw = self.inputs.new
        sonw = self.outputs.new
        sinw('VerticesSocket', "Verts Line A")
        sinw('VerticesSocket', "Center").prop_name = 'sphere_center'
        sinw('StringsSocket', "Radius").prop_name = 'radius'

        sonw('StringsSocket', "Intersect Num")
        sonw('VerticesSocket', "Intersection A")
        sonw('VerticesSocket', "Intersection B")

    def draw_buttons_ext(self, context, layout):
        '''draw buttons on the N-panel'''
        layout.prop(self, "tolerance")

    def get_data(self):
        '''get all data from sockets'''
        si = self.inputs
        verts_line = si['Verts Line A'].sv_get(default=[[]])
        center = si['Center'].sv_get(default=[[]])
        radius = si['Radius'].sv_get(default=[[]])

        return match_long_repeat([verts_line, center, radius])

    def process(self):
        '''main node function called every update'''
        so = self.outputs
        si = self.inputs
        if not (any(s.is_linked for s in so) and si[0].is_linked):
            return

        result = [[], [], []]
        gates = []
        gates.append(so['Intersect Num'].is_linked)
        gates.append(so['Intersection A'].is_linked)
        gates.append(so['Intersection B'].is_linked)

        group = self.get_data()

        for line, all_centers, all_radius in zip(*group):
            subgroup = match_long_repeat([all_centers, all_radius])
            subresult = [[], [], []]
            for center, radius in zip(*subgroup):
                compute_intersect_line_sphere(line, center, radius, subresult, gates, self.tolerance)
            for i, r in enumerate(result):
                if gates[i]:
                    r.append(subresult[i])
                    
        for i, r in enumerate(result):
            if gates[i]:
                so[i].sv_set(result[i])


def register():
    '''register class in Blender'''
    bpy.utils.register_class(SvIntersectLineSphereNode)


def unregister():
    '''unregister class in Blender'''
    bpy.utils.unregister_class(SvIntersectLineSphereNode)
