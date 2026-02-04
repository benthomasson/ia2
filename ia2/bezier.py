"""Bezier curves: drawing, paths, Coons patches, clipping."""

import cairo
import numpy as np

from ia2.draw import draw_line, draw_path
from ia2.math import RED, pi


def draw_bezier(anim, p0, p1, p2, p3, color, width=1, fill=None, fill_alpha=1, alpha=1):
    """Draw a cubic Bezier curve with control points."""
    ctx = anim.ctx
    ctx.move_to(*p0)
    ctx.curve_to(*p1, *p2, *p3)
    if fill:
        ctx.set_source_rgba(*fill, fill_alpha)
        ctx.fill_preserve()
    ctx.set_source_rgba(*color, alpha)
    ctx.set_line_width(width)
    ctx.stroke()
    if anim.debug or anim.selected:
        draw_line(anim, p0, p1, RED, 2)
        draw_line(anim, p2, p3, RED, 2)


def draw_bezier_path(anim, p0, points, color, width=10, alpha=1, fill=None, fill_alpha=1):
    """Draw a path of connected cubic Bezier curves.

    points is a list of (p1, p2, p3) control point triples.
    """
    if p0[0] is None:
        return
    anim.ctx.set_line_width(width)
    if fill:
        anim.ctx.move_to(*p0)
        last = p0
        last_p1 = None
        for p1, p2, p3 in points:
            if p1[0] is None:
                p1 = last
            if p3[0] is None:
                last_p1 = last_p1 or p1
                continue
            if p2[0] is None:
                p2 = p3
            p1 = last_p1 or p1
            anim.ctx.curve_to(*p1, *p2, *p3)
            last = p3
            last_p1 = None
        if isinstance(fill, cairo.Gradient):
            anim.ctx.set_source(fill)
            anim.ctx.fill()
            return
        else:
            anim.ctx.set_source_rgba(*fill, fill_alpha)
            anim.ctx.fill()
    anim.ctx.move_to(*p0)
    last = p0
    last_p1 = None
    for p1, p2, p3 in points:
        if p1[0] is None:
            p1 = last
        if p3[0] is None:
            last_p1 = last_p1 or p1
            continue
        if p2[0] is None:
            p2 = p3
        p1 = last_p1 or p1 or last
        anim.ctx.curve_to(*p1, *p2, *p3)
        last = p3
        last_p1 = None
    anim.ctx.set_source_rgba(*color, alpha)
    anim.ctx.stroke()
    if anim.debug or anim.selected:
        last = p0
        last_p1 = None
        for p1, p2, p3 in points:
            if p1[0] is None:
                p1 = last
            if p3[0] is None:
                last_p1 = last_p1 or p1
                continue
            if p2[0] is None:
                p2 = p3
            p1 = last_p1 or p1
            draw_line(anim, last, p1, RED, 2, alpha=0.5)
            draw_line(anim, p2, p3, RED, 2, alpha=0.5)
            last = p3
            last_p1 = None


def bezier_curve(control_points, num_points=100):
    """Generate points on a Bezier curve using de Casteljau's algorithm."""
    t_values = np.linspace(0, 1, num_points)

    def de_casteljau(t, points):
        while len(points) > 1:
            points = [
                (1 - t) * points[i] + t * points[i + 1] for i in range(len(points) - 1)
            ]
        return points[0]

    return [de_casteljau(t, control_points) for t in t_values]


def shade_coons_patch(anim, p0, points, colors, control_points=None):
    """Shade a Coons patch defined by Bezier boundary curves."""
    points = points[:4]
    pattern = cairo.MeshPattern()
    pattern.begin_patch()
    pattern.move_to(*p0)
    for p1, p2, p3 in points:
        pattern.curve_to(*p1, *p2, *p3)
    for i, color in enumerate(colors):
        pattern.set_corner_color_rgba(i, *color)
    if control_points:
        for i, point in enumerate(control_points):
            pattern.set_control_point(i, *point)
    pattern.end_patch()

    anim.ctx.move_to(*p0)
    for p1, p2, p3 in points:
        anim.ctx.curve_to(*p1, *p2, *p3)
    anim.ctx.set_source(pattern)
    anim.ctx.fill()

    if anim.debug or anim.selected:
        anim.ctx.move_to(*p0)
        for p1, p2, p3 in points:
            anim.ctx.curve_to(*p1, *p2, *p3)
        anim.ctx.set_dash([4.0])
        anim.ctx.set_source_rgb(*RED)
        anim.ctx.stroke()
        anim.ctx.set_dash([])
        for p1, p2, p3 in points:
            draw_line(anim, p0, p1, RED, 2)
            draw_line(anim, p2, p3, RED, 2)
            p0 = p3


def clip_bezier_path(anim, p, points):
    """Set a clipping region from a Bezier path."""
    if anim.construct:
        p0 = p
        for p1, p2, p3 in points:
            draw_line(anim, p0, p1, RED, 2)
            draw_line(anim, p2, p3, RED, 2)
            p0 = p3
        anim.ctx.move_to(*p0)
        for p1, p2, p3 in points:
            anim.ctx.curve_to(*p1, *p2, *p3)
        anim.ctx.set_dash([4.0])
        anim.ctx.set_source_rgb(*RED)
        anim.ctx.stroke()
        anim.ctx.set_dash([])
    p0 = p
    anim.ctx.move_to(*p0)
    for p1, p2, p3 in points:
        anim.ctx.curve_to(*p1, *p2, *p3)
    anim.ctx.clip()


def cut_bezier_path(anim, p, points, tlp=(-1000, -1000), width=2000, height=2000):
    """Set a clipping region that excludes a Bezier path (inverse clip)."""
    if anim.construct:
        p0 = p
        for p1, p2, p3 in points:
            draw_line(anim, p0, p1, RED, 2)
            draw_line(anim, p2, p3, RED, 2)
            p0 = p3
        p0 = p
        anim.ctx.move_to(*p0)
        for p1, p2, p3 in points:
            anim.ctx.curve_to(*p1, *p2, *p3)
        anim.ctx.line_to(*p0)
        anim.ctx.set_line_width(5)
        anim.ctx.set_dash([10.0])
        anim.ctx.set_source_rgb(*RED)
        anim.ctx.stroke()
        anim.ctx.set_dash([])

    p0 = p
    anim.ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    anim.ctx.rectangle(*tlp, width, height)
    anim.ctx.move_to(*p0)
    for p1, p2, p3 in points:
        anim.ctx.curve_to(*p1, *p2, *p3)
    anim.ctx.clip()
