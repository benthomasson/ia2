"""
Math utilities: angles, distances, interpolation, coordinate conversions.

All angles in radians, standard math convention (0 = right, pi/2 = down in screen coords).
Cairo uses a y-axis-down coordinate system.
"""

import math as _math

import numpy as np
from scipy.optimize import minimize

# Re-export common math constants and functions for convenience
pi = _math.pi
cos = _math.cos
sin = _math.sin
ceil = _math.ceil
atan2 = _math.atan2
acos = _math.acos
inf = _math.inf

# Color constants
RED = (1, 0, 0)
GREEN = (0, 1, 0)
BLUE = (0, 0, 1)
WHITE = (1, 1, 1)
BLACK = (0, 0, 0)
GRAY = (0.5, 0.5, 0.5)
GRAY10 = (0.1, 0.1, 0.1)
GRAY20 = (0.2, 0.2, 0.2)
GRAY30 = (0.3, 0.3, 0.3)
GRAY40 = (0.4, 0.4, 0.4)
GRAY50 = (0.5, 0.5, 0.5)
GRAY60 = (0.6, 0.6, 0.6)
GRAY70 = (0.7, 0.7, 0.7)
GRAY80 = (0.8, 0.8, 0.8)
GRAY90 = (0.9, 0.9, 0.9)
YELLOW = (1, 1, 0)
MAGENTA = (1, 0, 1)
CYAN = (0, 1, 1)
PURPLE = (0.5, 0, 0.5)
ORANGE = (1, 0.5, 0)
BROWN = (0.6, 0.3, 0.1)
SUB_PRIMARY_COLORS = [MAGENTA, CYAN, YELLOW]
ADD_PRIMARY_COLORS = [RED, YELLOW, BLUE]
SECONDARY_COLORS = [GREEN, PURPLE, ORANGE]


def rgb(r, g, b):
    """Convert RGB 0-255 values to 0-1 float values."""
    return r / 255, g / 255, b / 255


def polar2z(r, theta):
    """Convert polar coordinates to a complex number."""
    return r * np.exp(1j * theta)


def z2polar(z):
    """Convert a complex number to polar coordinates (radius, angle)."""
    return (np.abs(z), np.angle(z))


def cart2pol(x, y):
    """Convert Cartesian coordinates to polar coordinates (rho, phi)."""
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return (rho, phi)


def pol2cart(rho, phi):
    """Convert polar coordinates to Cartesian coordinates (x, y)."""
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return (x, y)


def radians(degrees):
    """Convert degrees to radians."""
    return degrees * np.pi / 180


def angle(p1, p2):
    """Calculate the angle from p1 to p2 in radians."""
    x1, y1 = p1
    x2, y2 = p2
    return _math.atan2(y2 - y1, x2 - x1)


def anglep(p1, p2):
    """Calculate the angle from p1 to p2 as a positive angle (0 to 2pi)."""
    x1, y1 = p1
    x2, y2 = p2
    a = _math.atan2(y2 - y1, x2 - x1)
    if a < 0:
        a += 2 * pi
    return a


def midpoint(p1, p2):
    """Calculate the midpoint between two points."""
    x1, y1 = p1
    x2, y2 = p2
    return x2 + (x1 - x2) / 2, y2 + (y1 - y2) / 2


def distance(p1, p2):
    """Calculate the Euclidean distance between two points."""
    x1, y1 = p1
    x2, y2 = p2
    return _math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def distance2(p1, p2):
    """Calculate the squared Euclidean distance between two points."""
    x1, y1 = p1
    x2, y2 = p2
    return (x2 - x1) ** 2 + (y2 - y1) ** 2


def slope(p1, p2):
    """Calculate the slope of the line between two points."""
    return (p2[1] - p1[1]) / (p2[0] - p1[0])


def linear_interpolate(start, end, t):
    """Interpolate linearly between start and end over t steps."""
    space = np.linspace(0, 1, int(t))
    return np.interp(space, [0, 1], [start, end])


def sin_interpolate(start, end, t):
    """Interpolate between start and end using a sinusoidal ease over t steps."""
    space = np.sin(np.linspace(-pi / 2, pi / 2, int(t)))
    return np.interp(space, [-1, 1], [start, end])


interpolate = sin_interpolate


def calculate_ellipse(center, radius_x, radius_y, n=360):
    """Calculate points on an ellipse perimeter."""
    points = []
    for a in range(0, 361, int(360 / n)):
        x = center[0] + radius_x * _math.cos(_math.radians(a))
        y = center[1] + radius_y * _math.sin(_math.radians(a))
        points.append((x, y))
    return points


def calculate_elliptical_arc(center, radius_x, radius_y, a1, a2, n=100):
    """Calculate points on an elliptical arc from angle a1 to a2."""
    points = []
    for i in range(0, n):
        a = a1 + (a2 - a1) * i / n
        x = center[0] + radius_x * _math.cos(a)
        y = center[1] + radius_y * _math.sin(a)
        points.append((x, y))
    return points


def closest_point_to_line(point, line_start, line_end):
    """Find the closest point on a line segment to a given point.

    Args are numpy arrays.
    """
    assert isinstance(point, np.ndarray)
    assert isinstance(line_start, np.ndarray)
    assert isinstance(line_end, np.ndarray)

    if np.array_equal(line_start, line_end):
        return line_start

    AB = line_end - line_start
    BE = point - line_end
    if np.dot(AB, BE) > 0:
        return line_end

    AE = point - line_start
    if np.dot(AB, AE) < 0:
        return line_start

    line_direction = line_end - line_start
    point_vector = point - line_start
    projection = np.dot(point_vector, line_direction) / np.dot(
        line_direction, line_direction
    )
    return line_start + projection * line_direction


def closest_point_on_circle(point, center, radius):
    """Find the closest point on a circle to a given point.

    Args are numpy arrays.
    """
    assert isinstance(point, np.ndarray)
    assert isinstance(center, np.ndarray)

    vector_to_point = point - center
    direction = vector_to_point / np.linalg.norm(vector_to_point)
    return center + direction * radius


def closest_point_on_ellipse(point, center, a, b):
    """Find the closest point on an ellipse to a given point.

    Args are numpy arrays. This is slow due to optimization.
    """
    assert isinstance(point, np.ndarray)
    assert isinstance(center, np.ndarray)

    given_point = point

    def objective(p):
        return ((p[0] - given_point[0]) ** 2) + ((p[1] - given_point[1]) ** 2)

    def ellipse_constraint(p):
        x, y = p
        return ((x - center[0]) ** 2) / (a**2) + ((y - center[1]) ** 2) / (b**2) - 1

    result = minimize(
        objective, point, constraints={"type": "eq", "fun": ellipse_constraint}
    )
    return result.x


def closest_point_on_bezier(point, control_points):
    """Find the closest point on a Bezier curve to a given point."""

    def bernstein(t, n, i):
        return _math.comb(n, i) * (t**i) * ((1 - t) ** (n - i))

    def bezier(t, points):
        n = len(points) - 1
        return np.sum([bernstein(t, n, i) * points[i] for i in range(n + 1)], axis=0)

    def objective(t, point, points):
        return np.linalg.norm(bezier(t, points) - point) ** 2

    result = minimize(
        objective, 0.5, args=(point, control_points), bounds=[(0, 1)]
    )
    return bezier(result.x[0], control_points)


def tangent_points(p, c, pr):
    """Find tangent points on a circle from an external point.

    Args:
        p: External point
        c: Center of circle
        pr: Radius of circle
    """
    a = distance(c, pr)
    if distance(p, c) > a:
        b = distance(p, c)
        th = acos(a / b)
        d = atan2(p[1] - c[1], p[0] - c[0])
        d1 = d + th
        d2 = d - th
        tp1 = [c[0] + a * cos(d1), c[1] + a * sin(d1)]
        tp2 = [c[0] + a * cos(d2), c[1] + a * sin(d2)]
        return tp1, tp2
    elif distance(p, c) == a:
        return p, p
    else:
        return None, None
