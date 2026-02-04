"""Create a simple static PNG image."""

from ia2.context import png
from ia2.draw import draw_circle, draw_text, paint_background
from ia2.math import BLACK, RED, WHITE

with png("my_image.png", (800, 600)) as img:
    paint_background(img, BLACK)
    draw_circle(img, (400, 300), 100, WHITE, width=5)
    draw_text(img, (400, 450), "Hello, World!", RED, font_size=48)
