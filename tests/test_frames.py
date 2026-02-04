"""Tests for ia2.frames: frame generators, StopAnimation, StopInteractive, wait."""

import io
from unittest.mock import MagicMock

import pytest

from ia2.draw import make_surface
from ia2.frames import StopAnimation, StopInteractive, frames, one_frame, wait
from ia2.types import Animation


@pytest.fixture
def mock_anim():
    """Create an Animation with a mock pipe for frame writing."""
    surface, ctx = make_surface(100, 100)
    pipe = MagicMock()
    pipe.write = MagicMock()
    anim = Animation(ctx, surface, pipe, fps=30, width=100, height=100)
    return anim


class TestFrames:
    def test_correct_frame_count(self, mock_anim):
        frame_list = list(frames(mock_anim, 1.0))  # 1 second at 30 fps
        assert len(frame_list) == 30

    def test_frame_numbers_sequential(self, mock_anim):
        frame_list = list(frames(mock_anim, 0.5))
        assert frame_list == list(range(15))

    def test_fractional_time(self, mock_anim):
        frame_list = list(frames(mock_anim, 0.1))  # 3 frames at 30 fps
        assert len(frame_list) == 3

    def test_writes_frames_to_pipe(self, mock_anim):
        for _ in frames(mock_anim, 0.5):
            pass
        assert mock_anim.pipe.write.call_count == 15


class TestOneFrame:
    def test_yields_exactly_one(self, mock_anim):
        frame_list = list(one_frame(mock_anim))
        assert len(frame_list) == 1

    def test_yields_zero(self, mock_anim):
        frame_list = list(one_frame(mock_anim))
        assert frame_list == [0]


class TestStopExceptions:
    def test_stop_animation_is_exception(self):
        assert issubclass(StopAnimation, Exception)

    def test_stop_interactive_is_exception(self):
        assert issubclass(StopInteractive, Exception)

    def test_stop_animation_can_be_raised(self):
        with pytest.raises(StopAnimation):
            raise StopAnimation()

    def test_stop_interactive_can_be_raised(self):
        with pytest.raises(StopInteractive):
            raise StopInteractive()


class TestWait:
    def test_wait_writes_correct_frames(self, mock_anim):
        result = wait(mock_anim, 1.0)
        assert result == 30
        assert mock_anim.pipe.write.call_count == 30

    def test_wait_fractional(self, mock_anim):
        result = wait(mock_anim, 0.5)
        assert result == 15
