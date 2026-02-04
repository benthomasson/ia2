"""Shared fixtures for ia2 tests."""

import cairo
import pytest

from ia2.draw import make_surface
from ia2.types import Image


@pytest.fixture
def surface_ctx():
    """Create a real 100x100 Cairo ImageSurface and Context."""
    surface, ctx = make_surface(100, 100)
    return surface, ctx


@pytest.fixture
def img(surface_ctx):
    """Create an Image instance wrapping a 100x100 surface."""
    surface, ctx = surface_ctx
    return Image(ctx, surface, 100, 100)
