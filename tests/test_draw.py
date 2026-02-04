"""Tests for ia2.draw: real-surface rendering, pixel spot-checks."""

import struct

import cairo
import pytest

from ia2.draw import (
    draw_arc,
    draw_circle,
    draw_construction_circle,
    draw_construction_line,
    draw_disk,
    draw_ellipse,
    draw_glow,
    draw_line,
    draw_path,
    draw_rect,
    draw_text,
    draw_vector,
    make_surface,
    paint_background,
)
from ia2.math import BLACK, BLUE, GREEN, RED, WHITE


def get_pixel(surface, x, y):
    """Read ARGB pixel from Cairo ImageSurface at (x, y)."""
    surface.flush()
    data = surface.get_data()
    stride = surface.get_stride()
    offset = y * stride + x * 4
    # Cairo ARGB32 is stored as B, G, R, A in memory (little-endian)
    b, g, r, a = struct.unpack_from("BBBB", data, offset)
    return (r, g, b, a)


def pixel_is_color(surface, x, y, expected_rgb, tolerance=30):
    """Check if pixel at (x,y) approximately matches expected color (0-255 RGB)."""
    r, g, b, a = get_pixel(surface, x, y)
    er, eg, eb = expected_rgb
    return abs(r - er) < tolerance and abs(g - eg) < tolerance and abs(b - eb) < tolerance


class TestMakeSurface:
    def test_returns_surface_and_context(self):
        surface, ctx = make_surface(100, 100)
        assert isinstance(surface, cairo.ImageSurface)
        assert isinstance(ctx, cairo.Context)

    def test_surface_dimensions(self):
        surface, ctx = make_surface(200, 150)
        assert surface.get_width() == 200
        assert surface.get_height() == 150


class TestPaintBackground:
    def test_white_background(self, img):
        paint_background(img, WHITE)
        r, g, b, a = get_pixel(img.surface, 50, 50)
        assert r == 255 and g == 255 and b == 255

    def test_red_background(self, img):
        paint_background(img, RED)
        r, g, b, a = get_pixel(img.surface, 50, 50)
        assert r == 255 and g == 0 and b == 0


class TestDrawDisk:
    def test_center_pixel_has_color(self, img):
        paint_background(img, BLACK)
        draw_disk(img, (50, 50), 20, RED, fill_alpha=1)
        assert pixel_is_color(img.surface, 50, 50, (255, 0, 0))


class TestDrawCircle:
    def test_center_is_background(self, img):
        paint_background(img, BLACK)
        draw_circle(img, (50, 50), 30, GREEN, width=2)
        # Center should still be black (no fill)
        r, g, b, a = get_pixel(img.surface, 50, 50)
        assert r < 30 and g < 30 and b < 30

    def test_edge_has_color(self, img):
        paint_background(img, BLACK)
        draw_circle(img, (50, 50), 20, GREEN, width=4)
        # Pixel on the edge (approximately at radius distance)
        assert pixel_is_color(img.surface, 70, 50, (0, 255, 0), tolerance=50)


class TestDrawLine:
    def test_midpoint_has_color(self, img):
        paint_background(img, BLACK)
        draw_line(img, (0, 50), (100, 50), RED, width=4)
        assert pixel_is_color(img.surface, 50, 50, (255, 0, 0))


class TestDrawRect:
    def test_interior_pixel(self, img):
        paint_background(img, BLACK)
        draw_rect(img, (20, 20), 60, 60, RED, width=2, fill=RED, fill_alpha=1)
        assert pixel_is_color(img.surface, 50, 50, (255, 0, 0))


class TestDrawText:
    def test_no_crash(self, img):
        paint_background(img, BLACK)
        draw_text(img, (10, 50), "Hello", WHITE, font_size=20)


class TestDrawPath:
    def test_no_crash(self, img):
        paint_background(img, BLACK)
        points = [(10, 10), (50, 90), (90, 10)]
        draw_path(img, points, RED, width=2)


class TestDrawEllipse:
    def test_no_crash(self, img):
        paint_background(img, BLACK)
        draw_ellipse(img, (50, 50), 30, 20, RED, width=2)


class TestDrawArc:
    def test_no_crash(self, img):
        paint_background(img, BLACK)
        import math
        draw_arc(img, (50, 50), 30, 0, math.pi, RED, width=2)


class TestDrawGlow:
    def test_no_crash(self, img):
        paint_background(img, BLACK)
        draw_glow(img, (50, 50), 5, 30, RED)


class TestDrawVector:
    def test_no_crash(self, img):
        paint_background(img, BLACK)
        draw_vector(img, (50, 50), 0, 30, RED, width=3)


class TestConstructionFunctions:
    def test_construction_line_skips_when_false(self, img):
        img.construct = False
        paint_background(img, BLACK)
        draw_construction_line(img, (0, 50), (100, 50))
        # Should still be black — nothing drawn
        r, g, b, a = get_pixel(img.surface, 50, 50)
        assert r < 30 and g < 30 and b < 30

    def test_construction_line_draws_when_true(self, img):
        img.construct = True
        paint_background(img, BLACK)
        draw_construction_line(img, (0, 50), (100, 50), color=RED, width=4)
        # Should have color now
        assert pixel_is_color(img.surface, 50, 50, (255, 0, 0), tolerance=100)

    def test_construction_circle_skips_when_false(self, img):
        img.construct = False
        paint_background(img, BLACK)
        draw_construction_circle(img, (50, 50), 20)
        r, g, b, a = get_pixel(img.surface, 70, 50)
        assert r < 30 and g < 30 and b < 30
