"""Tests for ia2.context: png() context manager."""

import os

import pytest

from ia2.context import png
from ia2.types import Image


class TestPng:
    def test_creates_file(self, tmp_path):
        outfile = str(tmp_path / "test.png")
        with png(filename=outfile, size=(100, 100)) as img:
            pass
        assert os.path.exists(outfile)

    def test_surface_dimensions(self, tmp_path):
        outfile = str(tmp_path / "test.png")
        with png(filename=outfile, size=(200, 150)) as img:
            assert img.width == 200
            assert img.height == 150

    def test_yields_image(self, tmp_path):
        outfile = str(tmp_path / "test.png")
        with png(filename=outfile, size=(100, 100)) as img:
            assert isinstance(img, Image)
