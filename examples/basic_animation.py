"""Simple animation: a disk moves across the screen."""

from ia2.context import ffmpeg_wav
from ia2.draw import draw_disk, paint_background
from ia2.frames import frames
from ia2.math import BLACK, WHITE, sin_interpolate

with ffmpeg_wav("animation.mp4", fps=30, size=(800, 600)) as anim:
    position = [100, 300]

    # Pre-compute the horizontal motion path
    x_values = sin_interpolate(100, 700, int(2.0 * 30))

    for frame in frames(anim, 3.0):
        # Move position during the first 2 seconds
        if frame < len(x_values):
            position[0] = x_values[frame]

        draw_disk(anim, position, 20, WHITE, fill_alpha=1)
