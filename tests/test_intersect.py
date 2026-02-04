"""Tests for ia2.intersect: circle-circle, line-line, line-circle, polygon clipping."""

import math

import numpy as np
import pytest

from ia2.intersect import (
    circle_intersect,
    clip_polygon,
    line_circle_intersect,
    line_intersect,
)


class TestCircleIntersect:
    def test_two_circles_intersecting(self):
        # Two unit circles offset by 1 along x
        result = circle_intersect((0, 0), 1, (1, 0), 1)
        assert result is not None
        p1, p2 = result
        # Both points should lie on both circles
        for p in (p1, p2):
            d0 = np.sqrt(p[0] ** 2 + p[1] ** 2)
            d1 = np.sqrt((p[0] - 1) ** 2 + p[1] ** 2)
            assert pytest.approx(d0, abs=0.01) == 1.0
            assert pytest.approx(d1, abs=0.01) == 1.0

    def test_two_circles_not_intersecting(self):
        result = circle_intersect((0, 0), 1, (10, 0), 1)
        assert result is None

    def test_two_circles_tangent(self):
        # Circles touching at exactly one point
        result = circle_intersect((0, 0), 1, (2, 0), 1)
        assert result is not None
        p1, p2 = result
        # Both returned points should be approximately the same
        np.testing.assert_allclose(p1, p2, atol=0.01)

    def test_two_identical_circles(self):
        # Same center and radius — returns None (d == 0)
        result = circle_intersect((0, 0), 1, (0, 0), 1)
        assert result is None


class TestLineIntersect:
    def test_two_lines_intersecting(self):
        # Line from (0,0)-(2,2) and line from (0,2)-(2,0)
        result = line_intersect((0, 0), (2, 2), (0, 2), (2, 0))
        assert result is not None
        x, y = result
        assert pytest.approx(x) == 1.0
        assert pytest.approx(y) == 1.0

    def test_two_parallel_lines(self):
        result = line_intersect((0, 0), (1, 1), (0, 1), (1, 2))
        assert result is None

    def test_perpendicular_lines(self):
        # Diagonal y=x and diagonal y=-x+2 (intersect at (1,1))
        result = line_intersect((0, 0), (2, 2), (0, 2), (2, 0))
        assert result is not None
        x, y = result
        assert pytest.approx(x) == 1.0
        assert pytest.approx(y) == 1.0

    def test_vertical_line(self):
        # Vertical line x=2 and horizontal line y=3
        result = line_intersect((2, -1), (2, 5), (0, 3), (4, 3))
        assert result is not None
        x, y = result
        assert pytest.approx(x) == 2.0
        assert pytest.approx(y) == 3.0

    def test_both_vertical_parallel(self):
        # Two vertical lines — parallel, no intersection
        result = line_intersect((1, 0), (1, 5), (3, 0), (3, 5))
        assert result is None


class TestLineCircleIntersect:
    def test_line_through_circle_center(self):
        result = line_circle_intersect((0, 0), (10, 0), (5, 0), 2)
        assert result is not None
        p1, p2 = result
        # Both points should be on the circle
        for p in (p1, p2):
            d = np.sqrt((p[0] - 5) ** 2 + p[1] ** 2)
            assert pytest.approx(d, abs=0.01) == 2.0

    def test_line_not_intersecting_circle(self):
        result = line_circle_intersect((0, 10), (10, 10), (5, 0), 2)
        assert result is None

    def test_vertical_line_through_circle(self):
        result = line_circle_intersect((0, -10), (0, 10), (0, 0), 5)
        assert result is not None
        p1, p2 = result
        for p in (p1, p2):
            d = np.sqrt(p[0] ** 2 + p[1] ** 2)
            assert pytest.approx(d, abs=0.01) == 5.0


class TestClipPolygon:
    def test_fully_inside(self):
        # Square fully inside the clip rectangle
        poly = [(10, 10), (90, 10), (90, 90), (10, 90)]
        result = clip_polygon(poly, 0, 0, 100, 100)
        assert len(result) == 4
        for p, expected in zip(result, poly):
            assert pytest.approx(p[0]) == expected[0]
            assert pytest.approx(p[1]) == expected[1]

    def test_fully_outside(self):
        poly = [(200, 200), (300, 200), (300, 300), (200, 300)]
        result = clip_polygon(poly, 0, 0, 100, 100)
        assert result == []

    def test_triangle_clipped_to_rect(self):
        # Triangle with one vertex above the clip rectangle
        poly = [(50, 10), (90, 90), (10, 90)]
        result = clip_polygon(poly, 0, 0, 100, 50)
        assert len(result) >= 3
        # All result points must be within bounds
        for x, y in result:
            assert x >= -0.01 and x <= 100.01
            assert y >= -0.01 and y <= 50.01

    def test_half_overlap(self):
        # Square half inside, half outside on the right
        poly = [(50, 25), (150, 25), (150, 75), (50, 75)]
        result = clip_polygon(poly, 0, 0, 100, 100)
        assert len(result) == 4
        # Right edge should be clipped to x=100
        for x, y in result:
            assert x >= 50 - 0.01
            assert x <= 100.01

    def test_corner_clip(self):
        # Square overlapping just the top-right corner of the clip rect
        poly = [(80, 80), (120, 80), (120, 120), (80, 120)]
        result = clip_polygon(poly, 0, 0, 100, 100)
        assert len(result) == 4
        for x, y in result:
            assert x >= 80 - 0.01 and x <= 100.01
            assert y >= 80 - 0.01 and y <= 100.01

    def test_polygon_larger_than_rect(self):
        # Polygon fully encloses the clip rect
        poly = [(-50, -50), (150, -50), (150, 150), (-50, 150)]
        result = clip_polygon(poly, 0, 0, 100, 100)
        assert len(result) == 4
        xs = sorted([p[0] for p in result])
        ys = sorted([p[1] for p in result])
        assert pytest.approx(xs[0]) == 0
        assert pytest.approx(xs[-1]) == 100
        assert pytest.approx(ys[0]) == 0
        assert pytest.approx(ys[-1]) == 100

    def test_preserves_area(self):
        # A polygon fully inside should preserve its area
        poly = [(20, 20), (80, 20), (80, 80), (20, 80)]
        result = clip_polygon(poly, 0, 0, 100, 100)
        # Shoelace formula
        def area(pts):
            n = len(pts)
            a = 0
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                a += x1 * y2 - x2 * y1
            return abs(a) / 2
        assert pytest.approx(area(result)) == area(poly)

    def test_single_edge_clip(self):
        # Square extending past left edge only
        poly = [(-20, 30), (50, 30), (50, 70), (-20, 70)]
        result = clip_polygon(poly, 0, 0, 100, 100)
        assert len(result) == 4
        for x, y in result:
            assert x >= -0.01

    def test_empty_polygon(self):
        result = clip_polygon([], 0, 0, 100, 100)
        assert result == []

    def test_nonzero_bounds(self):
        # Clip rect not at origin
        poly = [(150, 150), (250, 150), (250, 250), (150, 250)]
        result = clip_polygon(poly, 100, 100, 200, 200)
        assert len(result) == 4
        for x, y in result:
            assert x >= 100 - 0.01 and x <= 200.01
            assert y >= 100 - 0.01 and y <= 200.01
