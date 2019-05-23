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

from mathutils import Vector as V
from mathutils.geometry import  barycentric_transform
from numpy import cross, sqrt, zeros, float32, array, dot 
from numpy.linalg import norm, inv

import bpy
from bpy.props import FloatProperty, FloatVectorProperty, BoolProperty, EnumProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, match_long_repeat


def matrix_def(tri0, tri1, tri2):
    tri_normal = cross( tri1- tri0, tri2- tri0)
    magnitude = norm(tri_normal)
    tri_area = 0.5 * magnitude
    tri3 = tri0 + (tri_normal / magnitude)* sqrt(tri_area) 
    
    transform_matrix = zeros([3,3], dtype=float32)
    transform_matrix[0,:] = tri0 - tri3
    transform_matrix[1,:] = tri1 - tri3
    transform_matrix[2,:] = tri2 - tri3

    return transform_matrix, tri3
           
def compute_barycentric_transform_np(params, result, out_numpy):
    verts = array(params[0])
    tri_s = array(params[1])
    tri_d = array(params[2])
    
    transform_matrix_s, tri3_s = matrix_def(tri_s[0,:], tri_s[1,:], tri_s[2,:])
    transform_matrix_d, tri3_d = matrix_def(tri_d[0,:], tri_d[1,:], tri_d[2,:])

    barycentric_co = dot(inv(transform_matrix_s).T, (verts - tri3_s).T)
    cartesian = dot(barycentric_co.T, transform_matrix_d) + tri3_d
    result.append(cartesian if out_numpy else cartesian.tolist())

    
def compute_barycentric_transform_mu(params, result, out_numpy):
    tri_s = [V(v) for v in params[1]]
    tri_d = [V(v) for v in params[2]]
    sub_result = []
    for vert in params[0]:
        point_V = V(vert)
        transformed_vert = barycentric_transform(vert, tri_s[0], tri_s[1], tri_s[2], tri_d[0], tri_d[1], tri_d[2])
        sub_result.append(list(transformed_vert))
    result.append(sub_result)

    
class SvBarycentricTransformNode(bpy.types.Node, SverchCustomTreeNode):
    '''
    Triggers: Transform triangle based
    Tooltip: Performs barycentric transformation between two triangles.
    '''
    bl_idname = 'SvBarycentricTransformNode'
    bl_label = 'Barycentric Transform'
    bl_icon = 'MESH_DATA'

    implentation_modes = [
        ("NumPy", "NumPy", "Faster to transform heavy meshes", 0),
        ("MathUtils", "MathUtils", "Faster to transform light meshes", 1)]

    compute_distances = {
        "NumPy": compute_barycentric_transform_np,
        "MathUtils": compute_barycentric_transform_mu}

    output_numpy = BoolProperty(
        name='Output NumPy', description='Output NumPy arrays',
        default=False, update=updateNode)

    implementation = EnumProperty(
        name='Implementation', items=implentation_modes,
        description='Choose calculation method',
        default="NumPy", update=updateNode)

    def sv_init(self, context):
        '''create sockets'''
        sinw = self.inputs.new
        sonw = self.outputs.new
        sinw('VerticesSocket', 'Vertices')
        sinw('VerticesSocket', 'Verts Tri Source')
        sinw('VerticesSocket', 'Verts Tri Target')

        sonw('VerticesSocket', 'Vertices')
        
    def draw_buttons_ext(self, context, layout):
        '''draw buttons on the N-panel'''
        layout.prop(self, "implementation", expand=True)
        if self.implementation == "NumPy":
            layout.prop(self, "output_numpy", toggle=False)
            
    def get_data(self):
        '''get all data from sockets'''
        si = self.inputs
        verts_in = si['Vertices'].sv_get(default=[[]])
        verts_tri_s = si['Verts Tri Source'].sv_get(default=[[]])
        verts_tri_d = si['Verts Tri Target'].sv_get(default=[[]])

        return match_long_repeat([verts_in, verts_tri_s, verts_tri_d])

    def process(self):
        '''main node function called every update'''
        so = self.outputs
        si = self.inputs
        if not (any(s.is_linked for s in so) and all(s.is_linked for s in si)):
            return

        result = []
        group = self.get_data()
        func = self.compute_distances[self.implementation]
        out_numpy = self.output_numpy
        
        for params in zip(*group):
            func(params, result, out_numpy)
            

        so[0].sv_set(result)



def register():
    '''register class in Blender'''
    bpy.utils.register_class(SvBarycentricTransformNode)


def unregister():
    '''unregister class in Blender'''
    bpy.utils.unregister_class(SvBarycentricTransformNode)
