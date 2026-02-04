"""Tests for ia2.bezier: curve generation, drawing functions."""

import numpy as np
import pytest

from ia2.bezier import bezier_curve, draw_bezier, draw_bezier_path
from ia2.draw import paint_background
from ia2.math import BLACK, RED


class TestBezierCurve:
    def test_returns_correct_number_of_points(self):
        pts = [np.array([0.0, 0.0]), np.array([1.0, 2.0]),
               np.array([3.0, 2.0]), np.array([4.0, 0.0])]
        result = bezier_curve(pts, num_points=50)
        assert len(result) == 50

    def test_first_point_matches_p0(self):
        pts = [np.array([0.0, 0.0]), np.array([1.0, 2.0]),
               np.array([3.0, 2.0]), np.array([4.0, 0.0])]
        result = bezier_curve(pts, num_points=100)
        np.testing.assert_allclose(result[0], [0.0, 0.0], atol=1e-10)

    def test_last_point_matches_p3(self):
        pts = [np.array([0.0, 0.0]), np.array([1.0, 2.0]),
               np.array([3.0, 2.0]), np.array([4.0, 0.0])]
        result = bezier_curve(pts, num_points=100)
        np.testing.assert_allclose(result[-1], [4.0, 0.0], atol=1e-10)

    def test_straight_line_all_on_line(self):
        pts = [np.array([0.0, 0.0]), np.array([1.0, 1.0]),
               np.array([2.0, 2.0]), np.array([3.0, 3.0])]
        result = bezier_curve(pts, num_points=20)
        for p in result:
            # y should equal x for a straight diagonal
            assert pytest.approx(p[0], abs=1e-10) == p[1]

    def test_default_num_points(self):
        pts = [np.array([0.0, 0.0]), np.array([1.0, 2.0]),
               np.array([3.0, 2.0]), np.array([4.0, 0.0])]
        result = bezier_curve(pts)
        assert len(result) == 100

    def test_three_control_points(self):
        # Quadratic Bezier (3 control points)
        pts = [np.array([0.0, 0.0]), np.array([1.0, 2.0]), np.array([2.0, 0.0])]
        result = bezier_curve(pts, num_points=10)
        assert len(result) == 10
        np.testing.assert_allclose(result[0], [0.0, 0.0], atol=1e-10)
        np.testing.assert_allclose(result[-1], [2.0, 0.0], atol=1e-10)


class TestDrawBezier:
    def test_no_crash(self, img):
        paint_background(img, BLACK)
        draw_bezier(img, (10, 50), (30, 10), (70, 90), (90, 50), RED, width=2)

    def test_no_crash_with_fill(self, img):
        paint_background(img, BLACK)
        draw_bezier(img, (10, 50), (30, 10), (70, 90), (90, 50), RED,
                    width=2, fill=(0, 0, 1))


class TestDrawBezierPath:
    def test_no_crash(self, img):
        paint_background(img, BLACK)
        p0 = (10, 50)
        points = [
            ((20, 20), (40, 20), (50, 50)),
            ((60, 80), (80, 80), (90, 50)),
        ]
        draw_bezier_path(img, p0, points, RED, width=2)
