# /// script
# requires-python = ">=3.10"
# dependencies = ["ia2", "moderngl"]
#
# [tool.uv.sources]
# ia2 = { git = "https://github.com/benthomasson/ia2" }
# ///
"""OpenGL text orientation test: verify text renders right-side up."""

import time

from ia2.context import opengl_interactive
from ia2.draw import draw_text, paint_background
from ia2.math import BLUE, GREEN, RED, WHITE

with opengl_interactive(size=(600, 400), title="Text Orientation Test") as anim:
    start_time = time.time()

    while time.time() - start_time < 3.0:
        if anim.window.is_closing:
            break

        paint_background(anim, (0.2, 0.2, 0.3))

        draw_text(anim, (20, 30), "TOP-LEFT", WHITE, font_size=20)
        draw_text(anim, (450, 30), "TOP-RIGHT", RED, font_size=20)
        draw_text(anim, (20, 350), "BOTTOM-LEFT", GREEN, font_size=20)
        draw_text(anim, (420, 350), "BOTTOM-RIGHT", BLUE, font_size=20)

        draw_text(anim, (200, 180), "Text should be", WHITE, font_size=24)
        draw_text(anim, (180, 210), "RIGHT-SIDE UP!", WHITE, font_size=24)

        anim.window.process_events()

    print("Text orientation test completed.")
