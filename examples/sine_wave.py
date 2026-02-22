# /// script
# requires-python = ">=3.10"
# dependencies = ["ia2"]
#
# [tool.uv.sources]
# ia2 = { git = "https://github.com/benthomasson/ia2" }
# ///
"""Animate a scrolling sine wave."""

import math

from ia2.context import ffmpeg_wav
from ia2.draw import draw_path, paint_background
from ia2.frames import frames
from ia2.math import BLACK, WHITE

with ffmpeg_wav("sine_wave.mp4", fps=60) as anim:
    points = []

    for frame in frames(anim, 4.0):
        # Add new point to the wave
        x = frame * 4
        y = 300 + 100 * math.sin(frame * 0.1)
        points.append((x, y))

        # Draw the wave
        if len(points) > 1:
            draw_path(anim, points, WHITE, width=3)

        # Keep only recent points
        if len(points) > 200:
            points.pop(0)
