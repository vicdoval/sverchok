# This file is part of project Sverchok. It's copyrighted by the contributors
# recorded in the version control history of the file, available from
# its original location https://github.com/nortikin/sverchok/commit/master
#
# SPDX-License-Identifier: GPL3
# License-Filename: LICENSE


from mathutils import Vector, Matrix
from math import acos, pi
import numpy as np
from numpy.linalg import norm as np_norm
from sverchok.utils.sv_bmesh_utils import bmesh_from_pydata
from sverchok.utils.modules.matrix_utils import matrix_normal, vectors_to_matrix, vectors_center_axis_to_matrix

def edges_aux(vertices):
    '''create auxiliary edges array '''
    v_len = [len(v) for v in vertices]
    v_len_max = max(v_len)
    np_in = np.arange(v_len_max - 1)
    np_edges = np.array([np_in, np_in + 1]).T

    return [np_edges]

def edges_length(vertices, edges, sum_length=False, out_numpy=False):
    '''calculate edges length '''

    np_verts = np.array(vertices)
    if type(edges[0]) in (list, tuple):
        np_edges = np.array(edges)
    else:
        np_edges = edges[:len(vertices)-1, :]

    vect = np_verts[np_edges[:, 0], :] - np_verts[np_edges[:, 1], :]
    length = np.linalg.norm(vect, axis=1)
    if sum_length:
        length = np.sum(length)[np.newaxis]

    return length if out_numpy else length.tolist()


def edges_direction(vertices, edges, out_numpy=False):
    '''calculate edges direction '''

    np_verts = np.array(vertices)
    if type(edges[0]) in (list, tuple):
        np_edges = np.array(edges)
    else:
        np_edges = edges[:len(vertices)-1, :]

    vect = np_verts[np_edges[:, 1], :] - np_verts[np_edges[:, 0], :]
    dist = np_norm(vect, axis=1)
    vect_norm = vect/dist[:, np.newaxis]
    return vect_norm if out_numpy else vect_norm.tolist()

def adjacent_faces(edges, pols):
    '''calculate number of adjacent faces '''
    e_sorted = [sorted(e) for e in edges]
    ad_faces = [0 for e in edges]
    for pol in pols:
        for edge in zip(pol, pol[1:] + [pol[0]]):
            e_s = sorted(edge)
            if e_s in e_sorted:
                idx = e_sorted.index(e_s)
                ad_faces[idx] += 1
    return ad_faces

def adjacent_faces_comp(edges, pols):
    '''calculate adjacent faces '''
    e_sorted = [sorted(e) for e in edges]
    ad_faces = [[] for e in edges]
    for pol in pols:
        for edge in zip(pol, pol[1:] + [pol[0]]):
            e_s = sorted(edge)
            if e_s in e_sorted:
                idx = e_sorted.index(e_s)
                ad_faces[idx] += [pol]
    return ad_faces

def faces_angle(normals, edges, pols):
    ad_faces = adjacent_faces(edges, pols)
    e_sorted = [sorted(e) for e in edges]
    ad_faces = [[] for e in edges]
    for idp, pol in enumerate(pols):
        for edge in zip(pol, pol[1:] + [pol[0]]):
            e_s = sorted(edge)
            if e_s in e_sorted:
                idx = e_sorted.index(e_s)
                ad_faces[idx].append(idp)
    angles = []
    for edg in ad_faces:
        if len(edg) > 1:
            dot_p = Vector(normals[edg[0]]).dot(Vector(normals[edg[1]]))
            ang = acos(dot_p)
        else:
            ang = 2*pi
        angles.append(ang)
    return angles

def edges_normal(vertices, normals, edges, pols):
    # ad_faces = adjacent_faces(edges, pols)
    e_sorted = [sorted(e) for e in edges]
    ad_faces = [[] for e in edges]
    for idp, pol in enumerate(pols):
        for edge in zip(pol, pol[1:] + [pol[0]]):
            e_s = sorted(edge)
            if e_s in e_sorted:
                idx = e_sorted.index(e_s)
                ad_faces[idx].append(idp)
    result = []

    for edg_f, edg in zip(ad_faces, edges):
        if len(edg_f) > 1:
            edge_normal = (Vector(normals[edg_f[0]])+Vector(normals[edg_f[1]]))/2
        elif len(edg_f) == 1:
            edge_normal = Vector(normals[edg_f[0]])
        else:
            rot_mat = Matrix.Rotation(pi/2, 4, "Z")
            direc = (Vector(vertices[edg[1]])-Vector(vertices[edg[0]])).normalized()
            edge_normal = direc @ rot_mat
        result.append(tuple(edge_normal))
    return result


def edges_vertices(vertices, edges):
    verts = [[vertices[c] for c in e] for e in edges]
    eds = [[[0, 1]] for e in edges]
    vals = [verts, eds]
    return vals

def edges_normals_full(vertices, edges, faces):

    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    normals = [tuple(face.normal) for face in bm.faces]
    bm.free()
    vals = edges_normal(vertices, normals, edges, faces)

    return vals

def faces_angle_full(vertices, edges, faces):
    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    normals = [tuple(face.normal) for face in bm.faces]
    bm.free()
    vals = faces_angle(normals, edges, faces)
    return vals

def edge_is_boundary(vertices, edges, faces):
    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    vals = [edge.is_boundary for edge in bm.edges]
    bm.free()
    return vals

def edge_is_contiguous(vertices, edges, faces):
    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    vals = [edge.is_contiguous for edge in bm.edges]
    bm.free()
    return vals

def edge_is_convex(vertices, edges, faces):
    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    vals = [edge.is_convex for edge in bm.edges]
    bm.free()
    return vals

def edge_is_manifold(vertices, edges, faces):
    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    vals = [edge.is_manifold for edge in bm.edges]
    bm.free()
    return vals

def edges_is_wire(vertices, edges, faces):
    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    vals = [edge.is_wire for edge in bm.edges]
    bm.free()
    return vals

def edges_center(vertices, edges):
    vals = [tuple((Vector(vertices[e[0]])+Vector(vertices[e[1]]))/2) for e in edges]
    return vals

def edges_origin(vertices, edges):
    vals = [vertices[e[0]] for e in edges]
    return vals

def edges_end(vertices, edges):
    vals = [vertices[e[1]] for e in edges]
    return vals

def edges_matrix_center_ZY(vertices, edges):
    normal = edges_direction(vertices, edges, out_numpy=False)
    normal_v = [Vector(n) for n in normal]
    center = [(Vector(vertices[e[0]])+Vector(vertices[e[1]]))/2 for e in edges]
    vals = matrix_normal([center, normal_v], "Z", "Y")
    return vals

def edges_matrix_center_Z(vertices, edges, faces):
    direction = edges_direction(vertices, edges, out_numpy=False)
    direction_v = [Vector(d) for d in direction]
    center = [(Vector(vertices[e[0]]) + Vector(vertices[e[1]])) / 2 for e in edges]
    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    normals = [tuple(face.normal) for face in bm.faces]
    bm.free()
    ed_normals = edges_normal(vertices, normals, edges, faces)
    vals = vectors_center_axis_to_matrix(center, direction_v, ed_normals)
    return vals

def edges_matrix_center_X(vertices, edges, faces):
    p0 = [vertices[e[0]] for e in edges]
    center = [(Vector(vertices[e[0]])+ Vector(vertices[e[1]])) / 2 for e in edges]
    bm = bmesh_from_pydata(vertices, edges, faces, normal_update=True)
    normals = [tuple(face.normal) for face in bm.faces]
    bm.free()
    ed_normals = edges_normal(vertices, normals, edges, faces)
    vals = vectors_to_matrix(center, ed_normals, p0)
    return vals

edges_modes_dict = {
    'Geometry':           (100, 'vs', 'u', 've',  edges_vertices, 'Vertices Faces', 'Vertices of each edge'),
    'Length':             (101, 's', 's',  'ves', edges_length, 'Length', 'Edge length'),
    'Direction':          (102, 'v', '',   've',  edges_direction, 'Direction', 'Normalized Direction'),
    'Normal':             (103, 'v', '',   'vep', edges_normals_full, 'Normal', 'Edge Normal'),
    'Face Angle':         (104, 's', '',   'vep', faces_angle_full, 'Face Angle', 'Face angle'),
    'Is Boundary':        (105, 's', '',   'vep', edge_is_boundary, 'Is Boundary', 'Is Edge on mesh borders'),
    'Is Contiguous':      (106, 's', '',   'vep', edge_is_contiguous, 'Is Contuguous', 'Is Edge contiguous'),
    'Is Convex':          (107, 's', '',   'vep', edge_is_convex, 'Is_Convex', 'Is Edge Convex'),
    'Is Mainfold':        (108, 's', '',   'vep', edge_is_manifold, 'Is_Mainfold', 'Is Edge part of the Mainfold'),
    'Is Wire':            (109, 's', '',   'vep', edges_is_wire, 'Is_Wire', 'Has no related faces'),
    'Center':             (110, 'v', '',   've', edges_center, 'Center', 'Edges Midpoint'),
    'Origin':             (111, 'v', '',   've', edges_origin, 'Origin', 'Edges first point'),
    'End':                (112, 'v', '',   've', edges_end, 'End', 'Edges End point'),
    'Adjacent faces':     (113, 's', 'u',  'ep', adjacent_faces_comp, 'Faces', 'Adjacent faces'),
    'Adjacent faces Num': (114, 's', '',   'ep', adjacent_faces, 'Number', 'Adjacent faces number'),
    'Matrix Center ZY':   (115, 'm', 'u',  've', edges_matrix_center_ZY, 'Matrix', 'Matrix in center of edge. Z axis on edge. Y up'),
    'Matrix Center Z':    (116, 'm', 'u',  'vep', edges_matrix_center_Z,  'Matrix', 'Matrix in center of edge. Z axis on edge. Z in normal'),
    'Matrix Center X':    (117, 'm', 'u',  'vep', edges_matrix_center_X,  'Matrix', 'Matrix in center of edge. X axis on edge. Z in normal'),
}
