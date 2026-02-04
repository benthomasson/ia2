"""
Drawing primitives: shapes, text, gradients, construction helpers.

Consolidated from ia.lang — numbered variants merged into single functions.
"""

import cairo

from ia2.math import (
    BLUE,
    RED,
    acos,
    angle,
    atan2,
    calculate_ellipse,
    calculate_elliptical_arc,
    cos,
    distance,
    pi,
    sin,
)


def make_surface(width, height):
    """Create a Cairo surface and context with optimal settings."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_line_cap(cairo.LineCap.ROUND)
    ctx.set_line_join(cairo.LineJoin.ROUND)
    ctx.set_antialias(cairo.Antialias.BEST)
    return surface, ctx


def square_lines(anim):
    """Set square line caps and miter joins on the animation context."""
    anim.ctx.set_line_cap(cairo.LineCap.BUTT)
    anim.ctx.set_line_join(cairo.LineJoin.MITER)


def paint_background(anim, color):
    """Fill the entire background with a solid color."""
    anim.ctx.set_source_rgb(*color)
    anim.ctx.paint()


# --- Basic shapes ---

def draw_disk(anim, p, r, color, width=10, alpha=1, fill_alpha=0.5, fill=None):
    """Draw a filled circle (disk) with outline."""
    x, y = p
    ctx = anim.ctx
    if isinstance(fill, cairo.Gradient):
        ctx.set_source(fill)
        ctx.arc(x, y, r, 0, 2 * pi)
        ctx.fill()
    elif isinstance(color, cairo.Gradient):
        ctx.set_source(color)
        ctx.arc(x, y, r, 0, 2 * pi)
        ctx.stroke()
    elif isinstance(color, cairo.MeshPattern):
        ctx.set_source(color)
        ctx.arc(x, y, r, 0, 2 * pi)
        ctx.fill()
    else:
        if fill is None:
            fill = color
        ctx.set_source_rgba(*fill, fill_alpha)
        ctx.arc(x, y, r, 0, 2 * pi)
        ctx.fill_preserve()
        ctx.set_source_rgba(*color, alpha)
        ctx.set_line_width(width)
        ctx.stroke()


def draw_circle(anim, p, r, color, width=10, alpha=1, fill=None, fill_alpha=1):
    """Draw a circle with optional fill."""
    x, y = p
    ctx = anim.ctx
    if fill is not None:
        ctx.set_source_rgba(*fill, fill_alpha)
        ctx.arc(x, y, r, 0, 2 * pi)
        ctx.fill()
    if color is not None:
        ctx.set_source_rgba(*color, alpha)
        ctx.set_line_width(width)
        ctx.arc(x, y, r, 0, 2 * pi)
        ctx.stroke()


def draw_arc(anim, p, r, start, end, color, width=10, clockwise=True, alpha=1,
             fill=None, fill_alpha=1):
    """Draw an arc (portion of a circle) with optional fill."""
    x, y = p
    ctx = anim.ctx
    if clockwise:
        ctx.arc(x, y, r, start, end)
    else:
        ctx.arc_negative(x, y, r, start, end)
    if fill and isinstance(fill, cairo.Gradient):
        ctx.set_source(fill)
        ctx.fill()
    elif fill:
        ctx.set_source_rgba(*fill, fill_alpha)
        ctx.fill_preserve()
    ctx.set_source_rgba(*color, alpha)
    ctx.set_line_width(width)
    ctx.stroke()


def draw_rect(anim, p, w, h, color, width=10, alpha=1, fill=None, fill_alpha=0.5):
    """Draw a rectangle with optional fill."""
    x, y = p
    ctx = anim.ctx
    ctx.rectangle(x, y, w, h)
    ctx.set_line_width(width)
    if fill:
        ctx.set_source_rgba(*fill, fill_alpha)
        ctx.fill_preserve()
    ctx.set_source_rgba(*color, alpha)
    ctx.stroke()


def draw_rect2(anim, p1, p2, color, width=10, alpha=1, fill=None, fill_alpha=0.5):
    """Draw a rectangle defined by two opposite corner points."""
    x, y = p1
    w, h = p2[0] - p1[0], p2[1] - p1[1]
    draw_rect(anim, (x, y), w, h, color, width, alpha, fill=fill, fill_alpha=fill_alpha)


# --- Lines ---

def draw_line(anim, p1, p2, color, width=10, alpha=1):
    """Draw a straight line between two points."""
    x1, y1 = p1
    x2, y2 = p2
    anim.ctx.set_source_rgba(*color, alpha)
    anim.ctx.set_line_width(width)
    anim.ctx.move_to(x1, y1)
    anim.ctx.line_to(x2, y2)
    anim.ctx.stroke()


def draw_hash(anim, p2, p3, length, color, width=10, alpha=1):
    """Draw a hash mark perpendicular to line p2-p3 at the midpoint."""
    p = (p2[0] + (p3[0] - p2[0]) / 2, p2[1] + (p3[1] - p2[1]) / 2)
    line_angle = angle(p2, p3)
    ctx = anim.ctx
    ctx.save()
    ctx.translate(*p)
    ctx.rotate(line_angle)
    draw_line(anim, (0, -length), (0, length), color=color, width=width, alpha=alpha)
    ctx.restore()


def draw_right_angle(anim, p0, angle, size, color, line_width=10, alpha=1):
    """Draw a right angle marker at p0."""
    anim.ctx.save()
    anim.ctx.translate(*p0)
    anim.ctx.rotate(angle)
    anim.ctx.set_source_rgba(*color, alpha)
    anim.ctx.set_line_width(line_width)
    anim.ctx.move_to(size, 0)
    anim.ctx.line_to(size, size)
    anim.ctx.line_to(0, size)
    anim.ctx.stroke()
    anim.ctx.restore()


# --- Vector ---

def draw_vector(anim, p, angle, length, color, width=10, alpha=1):
    """Draw a vector (arrow) from p at a given angle and length."""
    if length < 0:
        length = abs(length)
        angle += pi
    x, y = p
    ctx = anim.ctx
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.set_line_width(width)
    ctx.set_source_rgba(*color, alpha)
    if length > 0:
        ctx.move_to(0, 0)
        ctx.line_to(0, -length)
        ctx.move_to(0.7 * width, -length + width * 0.9)
        ctx.line_to(0, -length)
        ctx.line_to(-0.7 * width, -length + width * 0.9)
        ctx.stroke()
    ctx.restore()


# --- Text ---

def draw_text(anim, p, text, color, font="", font_size=100, alpha=1):
    """Draw text at the specified position."""
    ctx = anim.ctx
    ctx.set_source_rgba(*color, alpha)
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(font_size)
    ctx.move_to(*p)
    ctx.show_text(text)
    ctx.new_path()


def draw_text2(anim, p, text, color, outline_color, font="", font_size=100, alpha=1,
               width=2):
    """Draw text with an outline."""
    ctx = anim.ctx
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(font_size)
    ctx.move_to(*p)
    ctx.text_path(text)
    ctx.set_source_rgba(*color, alpha)
    ctx.fill_preserve()
    ctx.set_source_rgba(*outline_color, alpha)
    ctx.set_line_width(width)
    ctx.stroke()
    ctx.move_to(*p)
    ctx.text_path(text)
    ctx.set_source_rgba(*color, alpha)
    ctx.fill()


# --- Paths ---

def draw_path(anim, points, color, width=10, alpha=1, fill=None, fill_alpha=1):
    """Draw a path connecting multiple points."""
    anim.ctx.set_line_width(width)
    if fill:
        first = True
        for point in points:
            if point[0] is None:
                continue
            if first:
                anim.ctx.move_to(*point)
                first = False
            else:
                anim.ctx.line_to(*point)
        anim.ctx.set_source_rgba(*fill, fill_alpha)
        anim.ctx.fill()
    first = True
    for point in points:
        if point[0] is None:
            continue
        if first:
            anim.ctx.move_to(*point)
            first = False
        else:
            anim.ctx.line_to(*point)
    anim.ctx.set_source_rgba(*color, alpha)
    anim.ctx.stroke()


def clip_path(anim, points):
    """Set a clipping region from a path of points."""
    anim.ctx.move_to(*points[0])
    for point in points[1:]:
        anim.ctx.line_to(*point)
    anim.ctx.clip()


def cut_path(anim, points, tlp=(-1000, -1000), width=2000, height=2000):
    """Set a clipping region that excludes a path (inverse clip)."""
    anim.ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    anim.ctx.rectangle(*tlp, width, height)
    anim.ctx.move_to(*points[0])
    for point in points[1:]:
        anim.ctx.line_to(*point)
    anim.ctx.clip()


def draw_points(anim, p, points, color, width=10, alpha=1):
    """Draw connected line segments through points, translated by p.

    If width is a list, each segment uses the corresponding width (variable-width mode).
    """
    ctx = anim.ctx
    ctx.save()
    ctx.translate(*p)
    if isinstance(width, (list, tuple)):
        previous = points[0]
        for w, point in zip(width[1:], points[1:]):
            ctx.move_to(*previous)
            ctx.line_to(*point)
            ctx.set_source_rgba(*color, alpha)
            ctx.set_line_width(w)
            ctx.stroke()
            previous = point
    else:
        ctx.move_to(*points[0])
        for point in points[1:]:
            ctx.line_to(*point)
        ctx.set_source_rgba(*color, alpha)
        ctx.set_line_width(width)
        ctx.stroke()
    ctx.restore()


def draw_variable_path(anim, points_with_width, color, alpha=1, fill=None, fill_alpha=1):
    """Draw a path where each point has (x, y, width)."""
    points = points_with_width
    if fill:
        anim.ctx.move_to(*points[0][:2])
        for point in points[1:]:
            anim.ctx.line_to(*point[:2])
        anim.ctx.set_source_rgba(*fill, fill_alpha)
        anim.ctx.fill()
    previous = points_with_width[0]
    anim.ctx.set_source_rgba(*color, alpha)
    for point in points[1:]:
        anim.ctx.set_line_width(previous[2])
        anim.ctx.move_to(*previous[:2])
        anim.ctx.line_to(*point[:2])
        anim.ctx.stroke()
        previous = point


# --- Ellipse ---

def draw_ellipse(anim, center, radius_x, radius_y, color, width=10, alpha=1,
                 fill=None, fill_alpha=1, angle=0, n=360):
    """Draw an ellipse with optional rotation and fill."""
    points = calculate_ellipse((0, 0), radius_x, radius_y, n=n)
    anim.ctx.save()
    anim.ctx.translate(*center)
    anim.ctx.rotate(angle)
    draw_path(anim, points, color, width, alpha, fill, fill_alpha)
    anim.ctx.restore()


def draw_elliptical_arc(anim, center, radius_x, radius_y, color, width=10, alpha=1,
                        fill=None, fill_alpha=1, angle=0, start_angle=0,
                        end_angle=2 * pi, n=100):
    """Draw an elliptical arc."""
    points = calculate_elliptical_arc(
        (0, 0), radius_x, radius_y, start_angle, end_angle, n
    )
    anim.ctx.save()
    anim.ctx.translate(*center)
    anim.ctx.rotate(angle)
    draw_path(anim, points, color, width, alpha, fill, fill_alpha)
    anim.ctx.restore()


# --- Gradients ---

def draw_glow(anim, p, r1, r2, color):
    """Draw a glowing effect using a radial gradient."""
    ctx = anim.ctx
    x, y = p
    gradient = cairo.RadialGradient(x, y, r1, x, y, r2)
    gradient.add_color_stop_rgba(1.0, *color, 0.0)
    gradient.add_color_stop_rgba(0.0, *color, 1.1)
    ctx.set_source(gradient)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.arc(x, y, r1, 0, 2 * pi)
    ctx.arc(x, y, r2, 0, 2 * pi)
    ctx.fill()


def draw_linear_gradient(anim, p1, p2, color1, color2, stop1=1.0, stop2=0.0,
                         alpha1=1.0, alpha2=1.0, width=10):
    """Draw a line with a linear gradient color transition."""
    ctx = anim.ctx
    gradient = cairo.LinearGradient(*p1, *p2)
    gradient.add_color_stop_rgba(stop1, *color1, alpha1)
    gradient.add_color_stop_rgba(stop2, *color2, alpha2)
    ctx.set_source(gradient)
    ctx.move_to(*p1)
    ctx.line_to(*p2)
    ctx.set_line_width(width)
    ctx.stroke()


def draw_linear_gradient_v(anim, p1, p2, color1, color2, stop1=1.0, stop2=0.0,
                           alpha1=1.0, alpha2=1.0, width=10):
    """Draw a vertical linear gradient rectangle."""
    ctx = anim.ctx
    gradient = cairo.LinearGradient(*p1, p1[0], p2[1])
    gradient.add_color_stop_rgba(stop1, *color1, alpha1)
    gradient.add_color_stop_rgba(stop2, *color2, alpha2)
    ctx.set_source(gradient)
    ctx.rectangle(*p1, p2[0] - p1[0], p2[1] - p1[1])
    ctx.fill()


def draw_linear_gradient_h(anim, p1, p2, color1, color2, stop1=1.0, stop2=0.0,
                           alpha1=1.0, alpha2=1.0, width=10):
    """Draw a horizontal linear gradient rectangle."""
    ctx = anim.ctx
    gradient = cairo.LinearGradient(*p1, p2[0], p1[1])
    gradient.add_color_stop_rgba(stop1, *color1, alpha1)
    gradient.add_color_stop_rgba(stop2, *color2, alpha2)
    ctx.set_source(gradient)
    ctx.rectangle(*p1, p2[0] - p1[0], p2[1] - p1[1])
    ctx.fill()


def draw_radial_gradient(anim, p, r1, r2, color1, color2, stop1=0.0, stop2=1.0,
                         alpha1=1.0, alpha2=1.0):
    """Draw a circle with a radial gradient color transition."""
    ctx = anim.ctx
    x, y = p
    gradient = cairo.RadialGradient(x, y, r1, x, y, r2)
    gradient.add_color_stop_rgba(stop1, *color1, alpha1)
    gradient.add_color_stop_rgba(stop2, *color2, alpha2)
    ctx.set_source(gradient)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.arc(x, y, r1, 0, 2 * pi)
    ctx.arc(x, y, r2, 0, 2 * pi)
    ctx.fill()


# --- Variable-width lines ---

def draw_circle_tangents(anim, c1, r1, c2, r2, color):
    """Draw the tangent band connecting two circles."""
    if r1 > r2:
        c1, c2 = c2, c1
        r1, r2 = r2, r1

    a = r2 - r1
    p = c1
    c = c2
    if distance(p, c) > a:
        b = distance(p, c)
        th = acos(a / b)
        d = atan2(p[1] - c[1], p[0] - c[0])
        d1 = d + th
        d2 = d - th
        tp1 = [c[0] + (a + r1) * cos(d1), c[1] + (a + r1) * sin(d1)]
        tp2 = [c[0] + (a + r1) * cos(d2), c[1] + (a + r1) * sin(d2)]
        tp3 = [p[0] + (r1) * cos(d1), p[1] + (r1) * sin(d1)]
        tp4 = [p[0] + (r1) * cos(d2), p[1] + (r1) * sin(d2)]
        points = [tp1, tp2, tp4, tp3]
        draw_path(anim, points, color, width=0, fill=color)


def draw_variable_line(anim, p1, p2, width1, width2, color):
    """Draw a line that varies in width from p1 to p2."""
    draw_circle_tangents(anim, p1, width1 / 2, p2, width2 / 2, color)
    draw_arc(anim, p1, width1 / 2, 0, 2 * pi, color, width=0, fill=color, fill_alpha=1)
    draw_arc(anim, p2, width2 / 2, 0, 2 * pi, color, width=0, fill=color, fill_alpha=1)


def draw_variable_path2(anim, path, color):
    """Draw a variable-width path where each point is (x, y, width)."""
    path = [p for p in path if p[0] is not None]
    if len(path) < 2:
        return
    for i in range(len(path) - 1):
        draw_variable_line(
            anim, path[i][:2], path[i + 1][:2], path[i][2], path[i + 1][2], color
        )


# --- Construction helpers ---

def draw_construction_line(anim, p1, p2, color=BLUE, width=2, dashed=True, dash=4):
    """Draw a construction line (dashed by default). Only draws when anim.construct is True."""
    if not anim.construct:
        return
    x1, y1 = p1
    x2, y2 = p2
    if dashed:
        anim.ctx.set_dash([dash])
    anim.ctx.set_source_rgba(*color, 1)
    anim.ctx.set_line_width(width)
    anim.ctx.move_to(x1, y1)
    anim.ctx.line_to(x2, y2)
    anim.ctx.stroke()
    anim.ctx.set_dash([])


def draw_construction_circle(anim, center, r, color=BLUE, width=2, dashed=True, dash=4):
    """Draw a construction circle (dashed by default). Only draws when anim.construct is True."""
    if not anim.construct:
        return
    x, y = center
    if dashed:
        anim.ctx.set_dash([dash])
    anim.ctx.set_source_rgba(*color, 1)
    anim.ctx.set_line_width(width)
    anim.ctx.arc(x, y, r, 0, 2 * pi)
    anim.ctx.stroke()
    anim.ctx.set_dash([])


def draw_construction_ellipse(anim, center, radius_x, radius_y, color=BLUE, width=10,
                              angle=0, dashed=True, dash=4):
    """Draw a construction ellipse. Only draws when anim.construct is True."""
    if not anim.construct:
        return
    points = calculate_ellipse((0, 0), radius_x, radius_y)
    anim.ctx.save()
    anim.ctx.translate(*center)
    anim.ctx.rotate(angle)
    if dashed:
        anim.ctx.set_dash([dash])
    draw_path(anim, points, color, width, alpha=1)
    anim.ctx.set_dash([])
    anim.ctx.restore()


def draw_construction_bezier(anim, p0, p1, p2, p3, color=BLUE, width=1, dashed=True,
                             dash=4):
    """Draw a construction Bezier curve. Only draws when anim.construct is True."""
    if not anim.construct:
        return
    ctx = anim.ctx
    ctx.move_to(*p0)
    ctx.curve_to(*p1, *p2, *p3)
    ctx.set_source_rgb(*color)
    if dashed:
        anim.ctx.set_dash([dash])
    ctx.set_line_width(width)
    ctx.stroke()
    if anim.debug or anim.selected:
        draw_line(anim, p0, p1, RED, 2)
        draw_line(anim, p2, p3, RED, 2)
    anim.ctx.set_dash([])


# --- Debug / annotation ---

def draw_point(anim, p, name, color, size, font_size=40):
    """Draw a labeled point with coordinates."""
    x, y = p
    x -= size // 2
    y -= size // 2
    draw_rect(anim, (x, y), size, size, color, 2)
    draw_text(anim, (x, y - font_size / 2), f"{name}", color, font_size=font_size)
    draw_text(
        anim,
        (x, y + font_size),
        f"{p[0]:.0f}, {p[1]:.0f}",
        color,
        font_size=font_size // 2,
    )
