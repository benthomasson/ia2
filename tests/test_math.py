"""Tests for ia2.math: colors, geometry, interpolation, coordinate conversions."""

import math

import numpy as np
import pytest

from ia2.math import (
    ADD_PRIMARY_COLORS,
    BLACK,
    BLUE,
    BROWN,
    CYAN,
    GRAY,
    GRAY10,
    GRAY20,
    GRAY30,
    GRAY40,
    GRAY50,
    GRAY60,
    GRAY70,
    GRAY80,
    GRAY90,
    GREEN,
    MAGENTA,
    ORANGE,
    PURPLE,
    RED,
    SECONDARY_COLORS,
    SUB_PRIMARY_COLORS,
    WHITE,
    YELLOW,
    angle,
    anglep,
    calculate_ellipse,
    calculate_elliptical_arc,
    cart2pol,
    closest_point_on_circle,
    closest_point_to_line,
    distance,
    distance2,
    interpolate,
    linear_interpolate,
    midpoint,
    pi,
    pol2cart,
    polar2z,
    radians,
    rgb,
    sin_interpolate,
    slope,
    tangent_points,
    z2polar,
)


# --- Color constants ---

class TestColorConstants:
    def test_red(self):
        assert RED == (1, 0, 0)

    def test_green(self):
        assert GREEN == (0, 1, 0)

    def test_blue(self):
        assert BLUE == (0, 0, 1)

    def test_white(self):
        assert WHITE == (1, 1, 1)

    def test_black(self):
        assert BLACK == (0, 0, 0)

    def test_gray(self):
        assert GRAY == (0.5, 0.5, 0.5)

    def test_yellow(self):
        assert YELLOW == (1, 1, 0)

    def test_magenta(self):
        assert MAGENTA == (1, 0, 1)

    def test_cyan(self):
        assert CYAN == (0, 1, 1)

    def test_purple(self):
        assert PURPLE == (0.5, 0, 0.5)

    def test_orange(self):
        assert ORANGE == (1, 0.5, 0)

    def test_brown(self):
        assert BROWN == (0.6, 0.3, 0.1)

    def test_all_colors_are_3_tuples(self):
        colors = [
            RED, GREEN, BLUE, WHITE, BLACK, GRAY,
            GRAY10, GRAY20, GRAY30, GRAY40, GRAY50,
            GRAY60, GRAY70, GRAY80, GRAY90,
            YELLOW, MAGENTA, CYAN, PURPLE, ORANGE, BROWN,
        ]
        for c in colors:
            assert len(c) == 3, f"{c} should have length 3"

    def test_color_palettes(self):
        assert len(SUB_PRIMARY_COLORS) == 3
        assert len(ADD_PRIMARY_COLORS) == 3
        assert len(SECONDARY_COLORS) == 3


# --- rgb ---

class TestRgb:
    def test_red_255(self):
        assert rgb(255, 0, 0) == (1.0, 0.0, 0.0)

    def test_mid_gray(self):
        r, g, b = rgb(128, 128, 128)
        assert pytest.approx(r, abs=0.01) == 128 / 255

    def test_black(self):
        assert rgb(0, 0, 0) == (0.0, 0.0, 0.0)


# --- Coordinate conversions ---

class TestCoordinateConversions:
    def test_radians_180(self):
        assert pytest.approx(radians(180)) == math.pi

    def test_radians_90(self):
        assert pytest.approx(radians(90)) == math.pi / 2

    def test_radians_360(self):
        assert pytest.approx(radians(360)) == 2 * math.pi

    def test_polar2z_z2polar_roundtrip(self):
        r, theta = 5.0, 1.2
        z = polar2z(r, theta)
        r2, theta2 = z2polar(z)
        assert pytest.approx(r2) == r
        assert pytest.approx(theta2) == theta

    def test_polar2z_unit(self):
        z = polar2z(1, 0)
        assert pytest.approx(z.real) == 1.0
        assert pytest.approx(z.imag, abs=1e-10) == 0.0

    def test_cart2pol_pol2cart_roundtrip(self):
        x, y = 3.0, 4.0
        rho, phi = cart2pol(x, y)
        x2, y2 = pol2cart(rho, phi)
        assert pytest.approx(x2) == x
        assert pytest.approx(y2) == y

    def test_cart2pol_known(self):
        rho, phi = cart2pol(1, 0)
        assert pytest.approx(rho) == 1.0
        assert pytest.approx(phi) == 0.0


# --- Angle functions ---

class TestAngle:
    def test_angle_right(self):
        assert pytest.approx(angle((0, 0), (1, 0))) == 0.0

    def test_angle_down(self):
        assert pytest.approx(angle((0, 0), (0, 1))) == math.pi / 2

    def test_angle_left(self):
        result = angle((0, 0), (-1, 0))
        assert pytest.approx(result) == math.pi

    def test_angle_up(self):
        result = angle((0, 0), (0, -1))
        assert pytest.approx(result) == -math.pi / 2

    def test_anglep_always_positive(self):
        # Up direction: atan2(-1, 0) = -pi/2, anglep should be 3pi/2
        result = anglep((0, 0), (0, -1))
        assert result >= 0
        assert pytest.approx(result) == 3 * math.pi / 2

    def test_anglep_right(self):
        result = anglep((0, 0), (1, 0))
        assert pytest.approx(result) == 0.0


# --- Geometry ---

class TestGeometry:
    def test_midpoint(self):
        assert midpoint((0, 0), (2, 2)) == (1, 1)

    def test_midpoint_negative(self):
        assert midpoint((-2, -2), (2, 2)) == (0, 0)

    def test_distance_345(self):
        assert pytest.approx(distance((0, 0), (3, 4))) == 5.0

    def test_distance_zero(self):
        assert distance((5, 5), (5, 5)) == 0.0

    def test_distance2_345(self):
        assert pytest.approx(distance2((0, 0), (3, 4))) == 25.0

    def test_slope_diagonal(self):
        assert slope((0, 0), (1, 1)) == 1.0

    def test_slope_horizontal(self):
        assert slope((0, 0), (5, 0)) == 0.0

    def test_slope_steep(self):
        assert slope((0, 0), (1, 2)) == 2.0


# --- Interpolation ---

class TestInterpolation:
    def test_linear_interpolate_basics(self):
        result = linear_interpolate(0, 10, 11)
        assert len(result) == 11
        assert pytest.approx(result[0]) == 0.0
        assert pytest.approx(result[-1]) == 10.0

    def test_linear_interpolate_midpoint(self):
        result = linear_interpolate(0, 10, 11)
        assert pytest.approx(result[5]) == 5.0

    def test_sin_interpolate_basics(self):
        result = sin_interpolate(0, 10, 11)
        assert len(result) == 11
        assert pytest.approx(result[0]) == 0.0
        assert pytest.approx(result[-1]) == 10.0

    def test_sin_interpolate_differs_from_linear(self):
        lin = linear_interpolate(0, 10, 11)
        sin_r = sin_interpolate(0, 10, 11)
        # Middle values should differ (sinusoidal ease)
        assert not pytest.approx(sin_r[3]) == lin[3]

    def test_interpolate_is_sin_interpolate(self):
        assert interpolate is sin_interpolate


# --- Ellipse ---

class TestEllipse:
    def test_calculate_ellipse_returns_points(self):
        points = calculate_ellipse((0, 0), 100, 50)
        assert len(points) > 0

    def test_calculate_ellipse_closed(self):
        points = calculate_ellipse((0, 0), 100, 50)
        # First and last point should be approximately equal (closed curve)
        assert pytest.approx(points[0][0], abs=1) == points[-1][0]
        assert pytest.approx(points[0][1], abs=1) == points[-1][1]

    def test_calculate_elliptical_arc_correct_count(self):
        points = calculate_elliptical_arc((0, 0), 100, 50, 0, math.pi, n=50)
        assert len(points) == 50


# --- Closest point functions ---

class TestClosestPoint:
    def test_closest_point_to_line_on_line(self):
        p = np.array([0.5, 0.0])
        start = np.array([0.0, 0.0])
        end = np.array([1.0, 0.0])
        result = closest_point_to_line(p, start, end)
        np.testing.assert_allclose(result, [0.5, 0.0])

    def test_closest_point_to_line_off_line(self):
        p = np.array([0.5, 1.0])
        start = np.array([0.0, 0.0])
        end = np.array([1.0, 0.0])
        result = closest_point_to_line(p, start, end)
        np.testing.assert_allclose(result, [0.5, 0.0])

    def test_closest_point_to_line_past_end(self):
        p = np.array([2.0, 0.0])
        start = np.array([0.0, 0.0])
        end = np.array([1.0, 0.0])
        result = closest_point_to_line(p, start, end)
        np.testing.assert_allclose(result, [1.0, 0.0])

    def test_closest_point_to_line_before_start(self):
        p = np.array([-1.0, 0.0])
        start = np.array([0.0, 0.0])
        end = np.array([1.0, 0.0])
        result = closest_point_to_line(p, start, end)
        np.testing.assert_allclose(result, [0.0, 0.0])

    def test_closest_point_on_circle(self):
        point = np.array([10.0, 0.0])
        center = np.array([0.0, 0.0])
        result = closest_point_on_circle(point, center, 5.0)
        np.testing.assert_allclose(result, [5.0, 0.0])

    def test_closest_point_on_circle_diagonal(self):
        point = np.array([10.0, 10.0])
        center = np.array([0.0, 0.0])
        result = closest_point_on_circle(point, center, 1.0)
        expected = np.array([1.0, 1.0]) / math.sqrt(2)
        np.testing.assert_allclose(result, expected, atol=1e-10)


# --- Tangent points ---

class TestTangentPoints:
    def test_tangent_points_known_case(self):
        # External point far from circle
        p = (10, 0)
        c = (0, 0)
        # pr is the radius point, not a scalar — tangent_points uses distance(c, pr)
        # distance(c, pr) = radius
        pr = (5, 0)  # radius = 5
        tp1, tp2 = tangent_points(p, c, pr)
        assert tp1 is not None
        assert tp2 is not None
        # Both tangent points should be on the circle (distance from center = 5)
        d1 = math.sqrt(tp1[0] ** 2 + tp1[1] ** 2)
        d2 = math.sqrt(tp2[0] ** 2 + tp2[1] ** 2)
        assert pytest.approx(d1, abs=0.01) == 5.0
        assert pytest.approx(d2, abs=0.01) == 5.0

    def test_tangent_points_inside_circle(self):
        p = (0, 0)
        c = (0, 0)
        pr = (5, 0)
        tp1, tp2 = tangent_points(p, c, pr)
        assert tp1 is None
        assert tp2 is None
