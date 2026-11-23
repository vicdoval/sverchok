# SPDX-License-Identifier: GPL-3.0-or-later
"""Polygon Grid geometry and topology regression tests; Blender not required.

Run: python3 tests/test_polygon_grid_optimized.py
"""
import ast
import math
from pathlib import Path
import unittest

import numpy as np

SOURCE = Path(__file__).resolve().parents[1] / "nodes/generators_extended/polygon_grid.py"
NAMES = {
    "triang_layout", "hexa_layout", "diamond_layout", "rect_layout",
    "generate_grid", "generate_tiles", "_joined_tiles"
}


def circle(radius, phase, nverts, matrix, mode):
    verts = [(math.sin(i * math.tau / nverts + phase) * radius,
              math.cos(i * math.tau / nverts + phase) * radius, 0.0)
             for i in range(nverts)]
    return (verts,
            [[i, (i + 1) % nverts] for i in range(nverts)],
            [list(range(nverts))])


def load_geometry():
    tree = ast.parse(SOURCE.read_text())
    funcs = [n for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name in NAMES]
    namespace = {"np": np, "sqrt": math.sqrt, "sin": math.sin,
                 "cos": math.cos, "radians": math.radians, "circle": circle}
    exec(compile(ast.Module(body=funcs, type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace


GEO = load_geometry()


class PolygonGridTests(unittest.TestCase):
    def test_all_layouts_and_tile_shapes(self):
        for shape, sides in (("TRIANGLE", 3), ("SQUARE", 4), ("HEXAGON", 6)):
            for layout in ("RECTANGLE", "TRIANGLE", "DIAMOND", "HEXAGON"):
                for angle in (0, 35, 90):
                    for center in (False, True):
                        grid = GEO["generate_grid"](
                            center, layout, shape, (1.25, angle, 4, 5), True)
                        self.assertTrue(grid)
                        for scale in (0., 0.8, 1.):
                            tile = circle(1.25 * scale,
                                          math.radians((45 if sides == 4 else 30) - angle),
                                          sides, None, "pydata")
                            v, e, f = GEO["_joined_tiles"](
                                tile, grid, 1.25, scale, sides, True, True, True)
                            self.assertEqual(len(f), len(grid))
                            self.assertEqual(len(e), len({tuple(sorted(edge)) for edge in e}))
                            self.assertTrue(all(0 <= i < len(v) for face in f for i in face))
                            self.assertTrue(all(0 <= i < len(v) for edge in e for i in edge))
                            for face, item in zip(f, grid):
                                cx, cy, rot = item[:3]
                                sign = -1 if sides == 3 and rot else 1
                                expected = np.array([
                                    (sign * x + cx, sign * y + cy, 0)
                                    for x, y, _ in tile[0]])
                                np.testing.assert_allclose(np.array(v)[face], expected,
                                                           rtol=1e-12, atol=1e-12)
                            if scale == 1.:
                                self.assertLess(len(v), len(grid) * sides)

    def test_sparse_outputs(self):
        grid = GEO["generate_grid"](True, "RECTANGLE", "SQUARE",
                                    (1.0, 0, 3, 3), True)
        tile = circle(1., math.radians(45), 4, None, "pydata")
        v, e, f = GEO["_joined_tiles"](tile, grid, 1., 1., 4,
                                       False, True, False)
        self.assertEqual(v, [])
        self.assertEqual(f, [])
        self.assertEqual(len(e), 24)

    def test_grid_centers_legacy_tuple_shape(self):
        for shape in ("HEXAGON", "SQUARE", "TRIANGLE"):
            for layout in ("RECTANGLE", "HEXAGON", "TRIANGLE", "DIAMOND"):
                basic = GEO["generate_grid"](True, layout, shape, (1., 15., 3, 4))
                enriched = GEO["generate_grid"](True, layout, shape,
                                                (1., 15., 3, 4), True)
                self.assertEqual(basic, [point[:3] for point in enriched])

    def test_zero_radius_and_separate(self):
        grid = GEO["generate_grid"](True, "RECTANGLE", "HEXAGON",
                                    (0., 0., 3, 3), True)
        tile = circle(0., math.radians(30), 6, None, "pydata")
        v, e, f = GEO["_joined_tiles"](tile, grid, 0., 1., 6, True, True, True)
        self.assertEqual(len(v), 1)
        self.assertEqual(e, [])
        self.assertEqual(f, [])
        v2, e2, f2 = GEO["generate_tiles"](
            (1., 0., 1., True, [grid], 6))
        self.assertEqual(len(v2[0]), 9)
        self.assertEqual(len(e2[0]), 9)
        self.assertEqual(len(f2[0]), 9)


if __name__ == "__main__":
    unittest.main()
