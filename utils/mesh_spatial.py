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

from mathutils import Vector
try:
    from mathutils.geometry import delaunay_2d_cdt
except ImportError:
    pass

from sverchok.utils.geom import linear_approximation
from sverchok.utils.sv_bmesh_utils import bmesh_from_pydata, pydata_from_bmesh

def single_face_delaunay(face_verts, add_verts, epsilon=1e-6):
    n = len(face_verts)
    face = list(range(n))
    edges = [(i,i+1) for i in range(n-1)] + [(n-1, 0)]
    plane = linear_approximation(face_verts).most_similar_plane()
    face_verts_2d = [plane.point_uv_projection(v) for v in face_verts]
    add_verts_2d = [plane.point_uv_projection(v) for v in add_verts]
    TRIANGLES = 1
    res = delaunay_2d_cdt(face_verts_2d + add_verts_2d, edges, [face], TRIANGLES, epsilon)
    new_verts_2d = res[0]
    new_edges = res[1]
    new_faces = res[2]
    new_add_verts = [tuple(plane.evaluate(p[0], p[1], normalize=True)) for p in new_verts_2d[n:]]
    return face_verts + new_add_verts, new_edges, new_faces

def mesh_insert_verts(verts, faces, add_verts_by_face, epsilon=1e-6):
    bm = bmesh_from_pydata(verts, [], [])
    for face_idx, face in enumerate(faces):
        add_verts = add_verts_by_face.get(face_idx)
        if not add_verts:
            continue
        n = len(face)
        face_verts = [verts[i] for i in face]
        new_face_verts, edges, new_faces = single_face_delaunay(face_verts, add_verts, epsilon)
        done_verts = dict((i, bm.verts[face[i]]) for i in range(n))
        for new_face in new_faces:
            bm_verts = []
            for i in new_face:
                bm_vert = done_verts.get(i)
                if not bm_vert:
                    bm_vert = bm.verts.new(new_face_verts[i])
                    bm.verts.index_update()
                    bm.verts.ensure_lookup_table()
                    done_verts[i] = bm_vert
                bm_verts.append(bm_vert)
                
            bm.faces.new(bm_verts)
            bm.faces.index_update()

    verts, edges, faces = pydata_from_bmesh(bm)
    bm.free()
    return verts, edges, faces

