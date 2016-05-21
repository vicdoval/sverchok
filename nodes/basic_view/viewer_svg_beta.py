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

import itertools

import bpy

from bpy.props import (
    BoolProperty, StringProperty, FloatProperty, IntProperty)

from sverchok.utils.sv_bmesh_utils import bmesh_from_pydata
from sverchok.utils.sv_viewer_utils import get_text

from sverchok.node_tree import (
    SverchCustomTreeNode, VerticesSocket, StringsSocket)

from sverchok.data_structure import (
    dataCorrect, fullList, updateNode)


''' zeffii may '16 '''

def SVG_SETUP(width, height):
    svg = """\
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="%s" height="%s">""" % (width, height)
    return svg

SVG_END = """\
</svg>
"""


class SvGBetaViewerNode(bpy.types.Node, SverchCustomTreeNode):

    bl_idname = 'SvGBetaViewerNode'
    bl_label = 'SvG viewer Beta'
    bl_icon = 'OUTLINER_OB_EMPTY'

    activate = BoolProperty(
        name='do_stuff',
        description='process incoming data - or not',
        default=True,
        update=updateNode)

    output_filename = StringProperty(default='dd', update=updateNode)

    def sv_init(self, context):
        self.use_custom_color = True
        inew = self.inputs.new
        inew('VerticesSocket', 'vertices')
        inew('StringsSocket', 'edges')
        inew('StringsSocket', 'faces')
        inew('StringsSocket', 'stroke_width')
        inew('VerticesSocket', 'stroke')
        inew('VerticesSocket', 'fill')

    def draw_buttons(self, context, layout):
        col = layout.column(align=True)
        col.prop(self, 'activate')
        row = col.row(align=True)
        row.prop(self, 'output_filename')

    def get_geometry_from_sockets(self):

        def get(socket):
            data = socket.sv_get(default=[])
            return dataCorrect(data)

        return [get(i) for i in self.inputs]

    def process(self):

        if (not self.inputs['vertices'].is_linked) or (not self.activate):
            return

        # m is used to denote the possibility of multiple lists per socket.
        geom = self.get_geometry_from_sockets()
        mverts, medges, mfaces, mline_width, mstroke, mfill = geom

        '''
        maxlen = max(len(mverts), *(map(len, mrest)))
        fullList(mverts, maxlen)
        for idx in range(3):
            if mrest[idx]:
                fullList(mrest[idx], maxlen)
        '''

        # for group, Verts in enumerate(mverts):
        #     if not Verts:
        #        continue
        texts = bpy.data.texts
        if mverts:
            text = get_text(self.output_filename)
            
            svg_strings = []
            svg_strings.append(SVG_SETUP(300, 400))
            for line in mverts:
                svg_strings.append(str(line))
            svg_strings.append(SVG_END)
            
            text.from_string('\n'.join(svg_strings))


def register():
    bpy.utils.register_class(SvGBetaViewerNode)


def unregister():
    bpy.utils.unregister_class(SvGBetaViewerNode)
