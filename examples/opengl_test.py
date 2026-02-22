# /// script
# requires-python = ">=3.10"
# dependencies = ["ia2", "moderngl"]
#
# [tool.uv.sources]
# ia2 = { git = "https://github.com/benthomasson/ia2" }
# ///
"""OpenGL interactive test: animated disk and rectangle."""

import time

from ia2.context import opengl_interactive
from ia2.draw import draw_disk, draw_rect, paint_background
from ia2.frames import save_frame
from ia2.math import BLACK, GREEN, RED

with opengl_interactive(size=(800, 600), title="OpenGL Test", fps=30) as anim:
    disk_pos = [100, 300]
    rect_pos = [300, 200]

    frame_count = 0
    start_time = time.time()

    while frame_count < 90:  # 3 seconds at 30 fps
        paint_background(anim, BLACK)

        # Animate positions
        disk_pos[0] = int(100 + 500 * (frame_count / 90.0))
        rect_pos[1] = int(200 + 100 * abs(0.5 - (frame_count % 60) / 60.0))

        draw_disk(anim, disk_pos, 40, RED, fill_alpha=1)
        draw_rect(anim, rect_pos, 80, 60, GREEN, width=2, fill=GREEN, fill_alpha=1)

        save_frame(anim)
        frame_count += 1

        anim.window.process_events()
        if anim.window.is_closing:
            break

    total_time = time.time() - start_time
    print(f"Frames: {frame_count}, Time: {total_time:.2f}s, "
          f"FPS: {frame_count / total_time:.1f}")
