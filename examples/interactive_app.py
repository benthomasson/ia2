"""Interactive app: a white disk follows the mouse cursor."""

import pygame

from ia2.context import pygame_interactive
from ia2.draw import draw_disk
from ia2.frames import one_frame
from ia2.math import WHITE

with pygame_interactive(size=(800, 600)) as anim:
    mouse_pos = [400, 300]

    while True:
        for event in anim.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    raise SystemExit
            if event.type == pygame.MOUSEMOTION:
                mouse_pos[:] = event.pos

        anim.events.clear()

        for frame in one_frame(anim):
            draw_disk(anim, mouse_pos, 30, WHITE, fill_alpha=1)
