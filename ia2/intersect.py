"""Geometric intersection functions: circle-circle, line-line, line-circle."""

import numpy as np


def circle_intersect(p0, r0, p1, r1):
    """Find the intersection points of two circles.

    Returns tuple of two points, or None if no intersection.
    """
    x0, y0 = p0
    x1, y1 = p1
    c0 = np.array([x0, y0])
    c1 = np.array([x1, y1])
    v = c1 - c0
    d = np.linalg.norm(v)

    if d > r0 + r1 or d == 0:
        return None

    u = v / d
    xvec = c0 + (d**2 - r1**2 + r0**2) * u / (2 * d)

    uperp = np.array([u[1], -u[0]])
    a = ((-d + r1 - r0) * (-d - r1 + r0) * (-d + r1 + r0) * (d + r1 + r0)) ** 0.5 / d
    return (xvec + a * uperp / 2, xvec - a * uperp / 2)


def line_intersect(p1, p2, p3, p4):
    """Find the intersection point of two lines.

    Returns (x, y) or None if parallel.
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    m1 = (y2 - y1) / (x2 - x1)
    m2 = (y4 - y3) / (x4 - x3)

    if m1 == m2:
        return None

    x = (m1 * x1 - m2 * x3 + y3 - y1) / (m1 - m2)
    y = m1 * (x - x1) + y1
    return (x, y)


def line_circle_intersect(p1, p2, c, r):
    """Find the intersection points of a line and a circle.

    Returns tuple of two points, or None if no intersection.
    """
    c = np.array(c)
    p1 = np.array(p1)
    p2 = np.array(p2)

    pt1 = p1 - c
    pt2 = p2 - c

    x1, y1 = pt1
    x2, y2 = pt2

    dx = x2 - x1
    dy = y2 - y1

    d_r_squared = dx**2 + dy**2
    determinant = x1 * y2 - x2 * y1
    discriminant = r**2 * d_r_squared - determinant**2

    if discriminant < 0:
        return None

    sqrt_discriminant = discriminant**0.5
    mp = np.array([-1, 1])
    sgn_dy = 1 if dy > 0 else -1

    coords_x = (determinant * dy + mp * sgn_dy * dx * sqrt_discriminant) / d_r_squared
    coords_y = (-determinant * dx + mp * np.abs(dy) * sqrt_discriminant) / d_r_squared

    at = np.array([coords_x[0], coords_y[0]])
    bt = np.array([coords_x[1], coords_y[1]])

    a = at + c
    b = bt + c

    return (a, b)
