"""Tests for ia2.intersect: circle-circle, line-line, line-circle intersections."""

import math

import numpy as np
import pytest

from ia2.intersect import circle_intersect, line_circle_intersect, line_intersect


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
