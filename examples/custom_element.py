"""Demonstrate a custom generator-based element.

Elements are Python generators that yield each frame, allowing
stateful animation with clean lifecycle management.
"""

from ia2.draw import draw_circle


def my_custom_element(anim, position, color):
    """A simple element that draws a circle each frame."""
    while True:
        draw_circle(anim, position, 50, color)
        yield  # Yield control back to the animation loop
