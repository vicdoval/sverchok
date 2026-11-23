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
import numpy as np
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty

from math import sqrt, sin, cos, radians

from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, match_long_repeat
from sverchok.ui.sv_icons import custom_icon
from sverchok.utils.geom import circle

grid_layout_items = [
    ("RECTANGLE", "Rectangle", "", custom_icon("SV_HEXA_GRID_RECTANGLE"), 0),
    ("TRIANGLE", "Triangle", "", custom_icon("SV_HEXA_GRID_TRIANGLE"), 1),
    ("DIAMOND", "Diamond", "", custom_icon("SV_HEXA_GRID_DIAMOND"), 2),
    ("HEXAGON", "Hexagon", "", custom_icon("SV_HEXA_GRID_HEXAGON"), 3)]
grid_type_items = [
    ("TRIANGLE", "Triangle", "", custom_icon("SV_TRIANGLE"), 0),
    ("SQUARE", "Square", "", custom_icon("SV_SQUARE"), 1),
    ("HEXAGON", "Hexagon", "", custom_icon("SV_HEXAGON"), 2)]
size_mode_items = [
    ("RADIUS", "Radius", "Define polygon by its radius", custom_icon("SV_RAD"), 0),
    ("SIDE", "Side", "Define polygon by its side", custom_icon("SV_SIDE"), 1)]


def triang_layout(settings, pol_type):
    '''Define triangular layout'''
    _, _, level = settings
    cols = level
    if pol_type == 'HEXAGON':
        rows = range(1, cols + 1)
        offset_y = range(cols)
        grid_center = [(level - 1) * 2 / 3, 0.0]
        tile_rotated = 0

    elif pol_type == 'TRIANGLE':
        rows = range(1, 2 * cols + 1, 2)
        offset_y = range(cols)
        grid_center = [(level - 1) * 2 / 3, 0.0]
        tile_rotated = [[(y) % 2 for y in range(rows[x])] for x in range(cols)]

    else: # pol_type == 'SQUARE':
        rows = range(1, 2 * cols + 2, 2)
        offset_y = range(0, 2 * cols, 2)
        grid_center = [(level - 1) / 2, 0.0]
        tile_rotated = 0
    return cols, rows, offset_y, grid_center, tile_rotated


def hexa_layout(settings, pol_type):
    '''Define hexagonal layout'''
    _, _, level = settings
    tile_rotated = 0
    if pol_type == 'HEXAGON':
        cols = 2 * level - 1
        rows = [cols - abs(level - 1 - l) for l in range(cols)]
        offset_y = [level - 1 - abs(level - 1 - l) for l in range(cols)]
        grid_center = [level - 1, (level - 1) / 2]

    elif pol_type == 'TRIANGLE':
        cols = 2 * level
        rows = [4 * level - abs(2*level - 1 - 2 * l) for l in range(cols)]
        offset_y = [2 * level - 0.5 - abs(level - 0.5 - l) for l in range(cols)]
        tile_rotated = [[(y + int(x / level)) % 2 for y in range(rows[x])] for x in range(cols)]
        grid_center = [level - 2 / 3, 0.0]

    else: # pol_type == 'SQUARE':
        cols = 2 * level
        rows = [3 * level - 1 - abs(2 * level - 1 - 2 * l) for l in range(cols)]
        offset_y = [2 * level - 1 - abs(2 * level - 1 - 2 * l) for l in range(cols)]
        grid_center = [level - 0.5, (level - 1) / 2]

    return cols, rows, offset_y, grid_center, tile_rotated


def diamond_layout(settings, pol_type):
    '''Define diamond layout'''
    _, _, level = settings
    tile_rotated = 0
    if pol_type == 'HEXAGON':
        cols = 2 * level - 1
        rows = [level - abs(level - 1 - l) for l in range(cols)]
        offset_y = [level - 1 - abs(level - 1 - l) for l in range(cols)]
        grid_center = [level - 1, 0.0]

    elif pol_type == 'TRIANGLE':
        cols = 2 * level
        rows = [cols - abs(2 * level - 1 - 2 * l) for l in range(cols)]
        offset_y = [level - 0.5 - abs(level - 0.5 - l) for l in range(cols)]
        tile_rotated = [[(y + int(x / level)) % 2 for y in range(rows[x])] for x in range(cols)]
        grid_center = [(level - 1) + 1/3.0, 0.0]

    else: # pol_type == 'SQUARE':
        cols = 2 * level - 1
        rows = [2 * level - 1 - abs(2 * level - 2 - 2 * l) for l in range(cols)]
        offset_y = [2 * level - 1 - abs(2 * level - 2 - 2 * l) for l in range(cols)]
        grid_center = [level - 1, 0.0]

    return cols, rows, offset_y, grid_center, tile_rotated


def rect_layout(settings, pol_type):
    '''Define rectangular layout'''
    _, _, numx, numy = settings
    cols = numx
    rows = [numy] * numx
    tile_rotated = 0
    if pol_type == 'HEXAGON':
        offset_y = [l % 2 for l in range(cols)]
        grid_center = [(numx - 1) / 2, (numy - 1.0 + 0.5 * (numx > 1)) / 2]

    elif pol_type == 'TRIANGLE':
        offset_y = [0 for l in range(cols)]
        grid_center = [(numx) / 2 - 2/3.0, (numy-1) / 2]
        tile_rotated = [[(x + y) % 2 for y in range(rows[x])] for x in range(cols)]

    else: # pol_type == 'SQUARE':
        offset_y = [0 for l in range(cols)]
        grid_center = [(numx-1) / 2, (numy-1) / 2]

    return cols, rows, offset_y, grid_center, tile_rotated



def generate_grid(center, layout, pol_type, settings, include_lattice=False):
    """Generate rotated tile centers in their original column-major order.

    With include_lattice=True, append integer (column, row, row-offset)
    coordinates for topology welding. These are independent of the
    floating-point radius and rotation.
    """
    r, angle = settings[:2]
    if pol_type == 'HEXAGON':
        dx = r * 3 / 2
        dy = r * sqrt(3)
        off_base = dy / 2
    elif pol_type == 'TRIANGLE':
        dx = r * 3 / 2
        dy = r * sqrt(3) / 2
        off_base = dy
    else:  # SQUARE
        dx = r * sqrt(2)
        dy = dx
        off_base = dy / 2

    if layout == 'TRIANGLE':
        cols, rows, offset_y, grid_center, _ = triang_layout(settings, pol_type)
    elif layout == 'HEXAGON':
        cols, rows, offset_y, grid_center, _ = hexa_layout(settings, pol_type)
    elif layout == 'DIAMOND':
        cols, rows, offset_y, grid_center, _ = diamond_layout(settings, pol_type)
    else:
        cols, rows, offset_y, grid_center, _ = rect_layout(settings, pol_type)

    cx = grid_center[0] * dx if center else (-dx / 2 if pol_type == 'SQUARE' else -dx * 2 / 3)
    cy = grid_center[1] * dy if center else 0

    # Some legacy layouts generate an extra unused row count; the first
    # 'cols' columns are the only ones included by the original loop.
    counts = np.asarray(rows[:cols], dtype=np.int64)
    ix = np.repeat(np.arange(cols, dtype=np.int64), counts)
    iy = np.arange(ix.size, dtype=np.int64) - np.repeat(np.cumsum(counts) - counts, counts)
    offsets = np.asarray(offset_y, dtype=np.int64)[ix]

    if pol_type == 'TRIANGLE':
        if layout == 'RECTANGLE':
            rotations = (ix + iy) % 2
        elif layout == 'TRIANGLE':
            rotations = iy % 2
        else:
            rotations = (iy + ix // settings[2]) % 2
        px = ix * dx - cx - r * 0.5 * rotations
    else:
        rotations = np.zeros(ix.size, dtype=np.int64)
        px = ix * dx - cx

    py = iy * dy - offsets * off_base - cy
    theta = radians(angle)
    cosa, sina = cos(theta), sin(theta)
    rx = px * cosa - py * sina
    ry = px * sina + py * cosa

    if include_lattice:
        return list(zip(rx.tolist(), ry.tolist(), rotations.tolist(),
                        ix.tolist(), iy.tolist(), offsets.tolist()))
    return list(zip(rx.tolist(), ry.tolist(), rotations.tolist()))


def _joined_tiles(tile, grid, radius, scale, sides, want_verts, want_edges, want_polys):
    """Build all faces directly; weld scale=1 tiles by exact lattice keys.

    No BMesh and no distance-dependent matching. Vertices retain the first
    corner occurrence order, and every face keeps the original tile order.
    """
    count = len(grid)
    if not count:
        return [], [], []

    # The former BMesh operation removes all degenerate faces at radius=0.
    if scale == 1.0 and radius == 0.0:
        return ([[0.0, 0.0, 0.0]] if want_verts else []), [], []

    if scale == 1.0:
        sites = np.asarray([item[3:6] for item in grid], dtype=np.int64)
        ix, iy, offsets = sites.T
        if sides == 6:
            key_x = 3 * ix[:, None] + np.array([1, 2, 1, -1, -2, -1])
            key_y = (2 * iy - offsets)[:, None] + np.array([1, 0, -1, -1, 0, 1])
        elif sides == 4:
            key_x = 2 * ix[:, None] + np.array([1, 1, -1, -1])
            key_y = (2 * iy - offsets)[:, None] + np.array([1, -1, -1, 1])
        else:
            rotation = np.fromiter((item[2] for item in grid), dtype=np.int64, count=count)
            sign = 1 - 2 * rotation
            key_x = (3 * ix - rotation)[:, None] + sign[:, None] * np.array([1, 1, -2])
            key_y = (iy - offsets)[:, None] + sign[:, None] * np.array([1, -1, 0])

        # A packed integer is faster than np.unique(axis=0) and cannot
        # collide within this grid, regardless of the world-space scale.
        row_span = int(key_y.max() - key_y.min() + 1)
        keys = ((key_x - key_x.min()) * row_span + key_y - key_y.min()).ravel()
        _, first, inverse = np.unique(keys, return_index=True, return_inverse=True)

        order = np.argsort(first)
        remap = np.empty(first.size, dtype=np.int64)
        remap[order] = np.arange(first.size)
        faces = remap[inverse].reshape(count, sides)
        first = first[order]
        vertex_count = first.size
    else:
        faces = np.arange(count * sides, dtype=np.int64).reshape(count, sides)
        vertex_count = count * sides

    verts = []
    if want_verts:
        centers = np.asarray([item[:2] for item in grid], dtype=float)
        local = np.asarray(tile[0], dtype=float)[:, :2]
        if sides == 3:
            sign = 1 - 2 * np.fromiter((item[2] for item in grid),
                                       dtype=np.int64, count=count)
        else:
            sign = np.ones(count, dtype=np.int64)
        all_verts = np.zeros((count, sides, 3), dtype=float)
        all_verts[:, :, :2] = centers[:, None, :] + sign[:, None, None] * local[None, :, :]
        flat_verts = all_verts.reshape(-1, 3)
        verts = (flat_verts[first] if scale == 1.0 else flat_verts).tolist()

    edges = []
    if want_edges:
        directed = np.stack((faces, np.roll(faces, -1, axis=1)), axis=-1).reshape(-1, 2)
        if scale == 1.0:
            low = np.minimum(directed[:, 0], directed[:, 1])
            high = np.maximum(directed[:, 0], directed[:, 1])
            keys = low * vertex_count + high
            _, first_edges = np.unique(keys, return_index=True)
            directed = directed[np.sort(first_edges)]
        edges = directed.tolist()

    return verts, edges, faces.tolist() if want_polys else []


def generate_tiles(tile_settings, requested=(True, True, True)):
    """Return one mesh (or list of tiles) for each input center grid."""
    radius, angle, scale, separate, grid_list, sides = tile_settings
    want_verts, want_edges, want_polys = requested
    local_angle = 45 if sides == 4 else 30
    tile = circle(radius * scale, radians(local_angle - angle), sides, None, 'pydata')

    vert_grid_list, edge_grid_list, poly_grid_list = [], [], []
    for grid in grid_list:
        if separate:
            tile_verts, tile_edges, tile_polys = tile
            vert_list, edge_list, poly_list = [], [], []
            for item in grid:
                cx, cy, rot = item[:3]
                if want_verts:
                    sign = -1 if sides == 3 and rot else 1
                    vert_list.append([(sign * x + cx, sign * y + cy, 0.0)
                                      for x, y, _ in tile_verts])
                if want_edges:
                    edge_list.append(tile_edges)
                if want_polys:
                    poly_list.append(tile_polys)
        else:
            vert_list, edge_list, poly_list = _joined_tiles(
                tile, grid, radius, scale, sides, want_verts, want_edges, want_polys)

        vert_grid_list.append(vert_list)
        edge_grid_list.append(edge_list)
        poly_grid_list.append(poly_list)

    return vert_grid_list, edge_grid_list, poly_grid_list

def tiles(vert_list, edge_list, poly_list, tile, grid):
    verts, edges, polys = tile
    for cx, cy, _ in grid:
        verts2 = [(x + cx, y + cy, 0.0) for x, y, _ in verts]

        vert_list.append(verts2)
        edge_list.append(edges)
        poly_list.append(polys)


def tiles_triangular(vert_list, edge_list, poly_list, tile, grid):
    verts, edges, polys = tile
    for cx, cy, rot in grid:
        inv = -1 if rot else 1
        verts2 = [(inv * x + cx, inv * y + cy, 0.0) for x, y, _ in verts]

        vert_list.append(verts2)
        edge_list.append(edges)
        poly_list.append(polys)


class SvPolygonGridNode(SverchCustomTreeNode, bpy.types.Node):
    """
    Triggers: Hexagonal, Triangular, Orthogonal,
    Tooltip: Create polygon array assambled to fill the plane. Triangles, Hexagons and Squares\n\tIn: Size, Scale, Angle, NumX/Y, Level\n\tParams: Type (Tri/Square/Hex), Layout (Rect, Tri, Diam, Hex)\n\tOut: Centers, Vertices, Edges, Polygons
    """
    bl_idname = 'SvPolygonGridNode'
    bl_label = 'Polygon Grid'
    bl_icon = 'OUTLINER_OB_EMPTY'
    sv_icon = 'SV_GRID'

    def update_layout(self, context):
        self.update_sockets()
        updateNode(self, context)

    gridType: EnumProperty(
        name="Type",
        description="Polygon Type",
        default="HEXAGON", items=grid_type_items,
        update=update_layout)

    gridLayout: EnumProperty(
        name="Layout",
        description="Polygon Layout",
        default="RECTANGLE", items=grid_layout_items,
        update=update_layout)

    sizeMode: EnumProperty(
        name="size_mode",
        description="Define tiles by",
        default="RADIUS", items=size_mode_items,
        update=update_layout)

    level: IntProperty(
        name="Level", description="Number of levels in non rectangular layouts",
        default=3, min=1, update=updateNode)

    numx: IntProperty(
        name="NumX", description="Number of points along X",
        default=7, min=1, update=updateNode)

    numy: IntProperty(
        name="NumY", description="Number of points along Y",
        default=6, min=1, update=updateNode)

    radius: FloatProperty(
        name="Size", description="Radius / Side of the grid tile",
        default=1.0, min=0.0, update=updateNode)

    angle: FloatProperty(
        name="Angle", description="Angle to rotate the grid and tiles",
        default=0.0, update=updateNode)

    scale: FloatProperty(
        name="Scale", description="Scale of the polygon tile",
        default=1.0, min=0.0, update=updateNode)

    center: BoolProperty(
        name="Center", description="Center grid around origin",
        default=True, update=updateNode)

    separate: BoolProperty(
        name="Separate", description="Separate tiles",
        default=False, update=updateNode)

    distanceName = "Radius"   ### WTF

    def sv_init(self, context):
        self.width = 170
        self.inputs.new('SvStringsSocket', "Radius").prop_name = 'radius'
        self.inputs.new('SvStringsSocket', "Scale").prop_name = 'scale'
        self.inputs.new('SvStringsSocket', "Angle").prop_name = 'angle'
        self.inputs.new('SvStringsSocket', "Level").prop_name = 'level'
        self.inputs.new('SvStringsSocket', "NumX").prop_name = 'numx'
        self.inputs.new('SvStringsSocket', "NumY").prop_name = 'numy'

        self.outputs.new('SvVerticesSocket', "Centers")
        self.outputs.new('SvVerticesSocket', "Vertices")
        self.outputs.new('SvStringsSocket', "Edges")
        self.outputs.new('SvStringsSocket', "Polygons")

        self.update_layout(context)

    def update_sockets(self):
        inputs = self.inputs
        named_sockets = ['NumX', 'NumY']


        if self.gridLayout == "RECTANGLE":
            if "Level" in inputs:
                inputs.remove(inputs["Level"])
            if "NumX" not in inputs:
                inputs.new("SvStringsSocket", "NumX").prop_name = "numx"
            if "NumY" not in inputs:
                inputs.new("SvStringsSocket", "NumY").prop_name = "numy"

        elif self.gridLayout in {"TRIANGLE", "DIAMOND", "HEXAGON"}:
            if "Level" not in inputs:
                inputs.new("SvStringsSocket", "Level").prop_name = "level"
            for socket_name in named_sockets:
                if socket_name in inputs:
                    inputs.remove(inputs[socket_name])

    def draw_buttons(self, context, layout):
        layout.prop(self, 'gridType', expand=False)
        layout.prop(self, 'gridLayout', expand=False)
        if self.gridType != "HEXAGON":
            layout.prop(self, 'sizeMode', expand=True)
        row = layout.row(align=True)
        row.prop(self, 'separate', toggle=True)
        row.prop(self, 'center', toggle=True)

    def process(self):
        # return if no outputs are connected
        if not any(s.is_linked for s in self.outputs):
            return

        if self.gridType == 'HEXAGON':
            sides = 6
        elif self.gridType == 'TRIANGLE':
            sides = 3
        elif self.gridType == 'SQUARE':
            sides = 4

        radius_factor = 2 * sin(radians(180/sides)) if self.gridType != 'HEXAGON' and self.sizeMode == 'SIDE' else 1

        # input values lists
        inputs = self.inputs
        input_level = inputs["Level"].sv_get()[0] if "Level" in inputs else [0]
        input_numx = inputs["NumX"].sv_get()[0] if "NumX" in inputs else [1]
        input_numy = inputs["NumY"].sv_get()[0] if "NumY" in inputs else [1]
        input_radius = inputs["Radius"].sv_get()[0]
        input_angle = inputs["Angle"].sv_get()[0]
        input_scale = inputs["Scale"].sv_get()[0]

        # sanitize the input values
        input_level = list(map(lambda x: max(1, x), input_level))
        input_numx = list(map(lambda x: max(1, x), input_numx))
        input_numy = list(map(lambda x: max(1, x), input_numy))
        input_radius = list(map(lambda x: max(0, x / radius_factor), input_radius))
        input_scale = list(map(lambda x: max(0, x), input_scale))

        # generate the vectorized grids
        param_list = []
        if self.gridLayout == 'RECTANGLE':
            param_list.extend([input_radius, input_angle, input_numx, input_numy])
        else:  # TRIANGLE, DIAMOND HEXAGON layouts
            param_list.extend([input_radius, input_angle, input_level])
        params = match_long_repeat(param_list)
        centers_socket, V, E, P = self.outputs[:]
        requested = (V.is_linked, E.is_linked, P.is_linked)
        needs_mesh = any(requested)
        grid_list = [
            generate_grid(self.center, self.gridLayout, self.gridType, args,
                          include_lattice=needs_mesh)
            for args in zip(*params)
        ]
        if centers_socket.is_linked:
            centers_socket.sv_set([
                [(x, y, 0.0) for x, y, *_ in grid] for grid in grid_list
            ])

        if not needs_mesh:
            return

        params = match_long_repeat([input_radius, input_angle, input_scale, grid_list])

        vert_list, edge_list, poly_list = [[], [], []]
        for r, a, s, grid in zip(*params):
            tile_settings = [r, a, s, self.separate, [grid], sides]

            verts, edges, polys = generate_tiles(tile_settings, requested)
            vert_list.extend(verts)
            edge_list.extend(edges)
            poly_list.extend(polys)

        if self.separate and len(vert_list) == 1:
            vert_list = vert_list[0]
            edge_list = edge_list[0]
            poly_list = poly_list[0]

        if V.is_linked:
            V.sv_set(vert_list)
        if E.is_linked:
            E.sv_set(edge_list)
        if P.is_linked:
            P.sv_set(poly_list)


def register():
    bpy.utils.register_class(SvPolygonGridNode)


def unregister():
    bpy.utils.unregister_class(SvPolygonGridNode)
