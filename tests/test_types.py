"""Tests for ia2.types: type construction, slots, Scene, AnimationSequence beat properties."""

import cairo
import numpy as np
import pytest

from ia2.draw import make_surface
from ia2.types import (
    Animation,
    AnimationSequence,
    Element,
    Image,
    MemoryMap,
    MemoryRange,
    Scene,
    Sequence,
)


@pytest.fixture
def surface_and_ctx():
    return make_surface(100, 100)


class TestAnimation:
    def test_construct(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        anim = Animation(ctx, surface, None, 30, 100, 100)
        assert anim.fps == 30
        assert anim.width == 100
        assert anim.height == 100
        assert anim.debug is False
        assert anim.construct is False

    def test_slots(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        anim = Animation(ctx, surface, None, 30, 100, 100)
        with pytest.raises(AttributeError):
            anim.nonexistent = True


class TestImage:
    def test_construct(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        img = Image(ctx, surface, 100, 100)
        assert img.width == 100
        assert img.fps == 1
        assert img.debug is False

    def test_slots(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        img = Image(ctx, surface, 100, 100)
        with pytest.raises(AttributeError):
            img.nonexistent = True


class TestSequence:
    def test_construct(self):
        data = np.zeros(44100, dtype=np.float32)
        seq = Sequence(data, 120, 44100, 30)
        assert seq.tempo == 120
        assert seq.rate == 44100
        assert seq.current_frame == 0


class TestAnimationSequence:
    def test_construct(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        data = np.zeros(44100, dtype=np.float32)
        anim = AnimationSequence(ctx, surface, None, 100, 100, 60, data, 120, 44100, 60)
        assert anim.fps == 60
        assert anim.tempo == 120

    def test_beat_at_120_bpm(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        data = np.zeros(44100, dtype=np.float32)
        anim = AnimationSequence(ctx, surface, None, 100, 100, 60, data, 120, 44100, 60)
        assert pytest.approx(anim.beat) == 0.5

    def test_whole_at_120_bpm(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        data = np.zeros(44100, dtype=np.float32)
        anim = AnimationSequence(ctx, surface, None, 100, 100, 60, data, 120, 44100, 60)
        assert pytest.approx(anim.whole) == 2.0

    def test_half_at_120_bpm(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        data = np.zeros(44100, dtype=np.float32)
        anim = AnimationSequence(ctx, surface, None, 100, 100, 60, data, 120, 44100, 60)
        assert pytest.approx(anim.half) == 1.0

    def test_quarter_equals_beat(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        data = np.zeros(44100, dtype=np.float32)
        anim = AnimationSequence(ctx, surface, None, 100, 100, 60, data, 120, 44100, 60)
        assert anim.quarter == anim.beat

    def test_eighth(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        data = np.zeros(44100, dtype=np.float32)
        anim = AnimationSequence(ctx, surface, None, 100, 100, 60, data, 120, 44100, 60)
        assert pytest.approx(anim.eighth) == 0.25

    def test_sixteenth(self, surface_and_ctx):
        surface, ctx = surface_and_ctx
        data = np.zeros(44100, dtype=np.float32)
        anim = AnimationSequence(ctx, surface, None, 100, 100, 60, data, 120, 44100, 60)
        assert pytest.approx(anim.sixteenth) == 0.125


class TestElement:
    def test_construct(self):
        gen = iter([1, 2, 3])
        e = Element("test", gen)
        assert e.name == "test"
        assert e.visible is True
        assert e.points == []

    def test_iter(self):
        gen = iter([1, 2, 3])
        e = Element("test", gen)
        name, generator, visible = e
        assert name == "test"
        assert visible is True

    def test_repr(self):
        gen = iter([])
        e = Element("test", gen)
        assert "Element(test" in repr(e)

    def test_getitem(self):
        gen = iter([])
        e = Element("test", gen, visible=False)
        assert e[0] == "test"
        assert e[1] is gen
        assert e[2] is False

    def test_getitem_out_of_range(self):
        gen = iter([])
        e = Element("test", gen)
        with pytest.raises(IndexError):
            e[3]


class TestScene:
    def test_dict_access(self):
        s = Scene()
        assert s["x_angle"] == 0
        assert s["scale"] == 1
        assert s["projection"] == "isometric"

    def test_custom_values(self):
        s = Scene(x_angle=1.5, scale=2.0, projection="perspective")
        assert s["x_angle"] == 1.5
        assert s["scale"] == 2.0
        assert s["projection"] == "perspective"

    def test_default_values(self):
        s = Scene()
        assert s["focal_length"] == 1000
        assert s["z_offset"] == 100
        assert s["rotation_order"] == "xyz"
        assert s["p"] == (0, 0)

    def test_is_dict(self):
        s = Scene()
        assert isinstance(s, dict)


class TestMemoryRange:
    def test_getitem(self):
        mr = MemoryRange("data", 4, 10)
        assert mr[0] == "data"
        assert mr[1] == 4
        assert mr[2] == 10

    def test_getitem_out_of_range(self):
        mr = MemoryRange("data", 4, 10)
        with pytest.raises(IndexError):
            mr[3]

    def test_slots(self):
        mr = MemoryRange("data", 4, 10)
        assert mr.name == "data"
        assert mr.size == 4
        assert mr.n == 10


class TestMemoryMap:
    def test_len(self):
        mm = MemoryMap([("a", 4, 2), ("b", 8, 1)])
        assert len(mm) == 16  # 4*2 + 8*1

    def test_slices(self):
        mm = MemoryMap([("a", 4, 3)])
        slices = mm.slices("a")
        assert slices == [[0, 4], [4, 8], [8, 12]]

    def test_empty(self):
        mm = MemoryMap()
        assert len(mm) == 0

    def test_multiple_ranges(self):
        mm = MemoryMap([("x", 2, 2), ("y", 3, 1)])
        assert len(mm) == 7  # 2*2 + 3*1
        assert mm.slices("x") == [[0, 2], [2, 4]]
        assert mm.slices("y") == [[4, 7]]
