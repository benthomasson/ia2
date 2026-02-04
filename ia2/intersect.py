"""Geometric intersection functions: circle-circle, line-line, line-circle, polygon clipping."""

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

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)
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


def clip_polygon(poly, xmin, ymin, xmax, ymax):
    """Clip a polygon to an axis-aligned rectangle using Sutherland-Hodgman.

    Args:
        poly: List of (x, y) vertex tuples.
        xmin, ymin, xmax, ymax: Rectangle bounds.

    Returns:
        List of (x, y) tuples for the clipped polygon, or [] if fully outside.
    """
    def _clip_edge(pts, side, val):
        if not pts:
            return []
        out = []
        for i in range(len(pts)):
            curr = pts[i]
            prev = pts[i - 1]
            c_in = _inside(curr, side, val)
            p_in = _inside(prev, side, val)
            if c_in:
                if not p_in:
                    out.append(_intersect(prev, curr, side, val))
                out.append(curr)
            elif p_in:
                out.append(_intersect(prev, curr, side, val))
        return out

    result = list(poly)
    for side, val in [('L', xmin), ('R', xmax), ('B', ymin), ('T', ymax)]:
        result = _clip_edge(result, side, val)
        if not result:
            return []
    return result


def _inside(p, side, val):
    if side == 'L': return p[0] >= val
    if side == 'R': return p[0] <= val
    if side == 'B': return p[1] >= val
    if side == 'T': return p[1] <= val


def _intersect(p1, p2, side, val):
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    if side in ('L', 'R'):
        if abs(dx) < 1e-12:
            return (val, y1)
        t = (val - x1) / dx
        return (val, y1 + t * dy)
    else:
        if abs(dy) < 1e-12:
            return (x1, val)
        t = (val - y1) / dy
        return (x1 + t * dx, val)
