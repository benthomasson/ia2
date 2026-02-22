# /// script
# requires-python = ">=3.10"
# dependencies = ["ia2"]
#
# [tool.uv.sources]
# ia2 = { git = "https://github.com/benthomasson/ia2" }
# ///
"""Pygame input demo: keyboard movement and mouse click to create disks."""

import time

import pygame

from ia2.context import pygame_interactive
from ia2.draw import draw_disk, draw_text, paint_background
from ia2.frames import one_frame
from ia2.math import BLACK, BLUE, GREEN, RED, WHITE

with pygame_interactive(size=(800, 600), title="Pygame Input Demo") as anim:
    player_pos = [400, 300]

    # Track mouse-created disks as (position, color) pairs
    mouse_disks = []

    last_mouse_click = 0
    total_disks_created = 0

    while True:
        for event in anim.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    player_pos[1] = max(25, player_pos[1] - 10)
                elif event.key == pygame.K_s:
                    player_pos[1] = min(anim.height - 25, player_pos[1] + 10)
                elif event.key == pygame.K_a:
                    player_pos[0] = max(25, player_pos[0] - 10)
                elif event.key == pygame.K_d:
                    player_pos[0] = min(anim.width - 25, player_pos[0] + 10)
                elif event.key == pygame.K_r:
                    mouse_disks.clear()
                    total_disks_created = 0
                elif event.key in [pygame.K_q, pygame.K_ESCAPE]:
                    raise SystemExit

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    colors = [RED, GREEN, BLUE]
                    color = colors[total_disks_created % len(colors)]
                    mouse_disks.append((list(event.pos), color))
                    total_disks_created += 1
                    last_mouse_click = time.time()

                    if len(mouse_disks) > 20:
                        mouse_disks.pop(0)

        anim.events.clear()

        for frame in one_frame(anim):
            paint_background(anim, BLACK)

            # Player disk
            draw_disk(anim, player_pos, 25, WHITE, fill_alpha=1)

            # Mouse-created disks
            for pos, color in mouse_disks:
                draw_disk(anim, pos, 20, color, fill_alpha=1)

            # UI text
            draw_text(anim, (20, 30), "Pygame Input Demo", WHITE, font_size=24)
            draw_text(anim, (20, 70), "WASD: Move player (white disk)", WHITE, font_size=16)
            draw_text(anim, (20, 95), "CLICK: Create colored disks", WHITE, font_size=16)
            draw_text(anim, (20, 120), "R: Reset all disks", WHITE, font_size=16)
            draw_text(anim, (20, 145), "Q/ESC: Quit", WHITE, font_size=16)

            draw_text(anim, (20, 200),
                      f"Player: ({player_pos[0]}, {player_pos[1]})", WHITE, font_size=14)
            draw_text(anim, (20, 220),
                      f"Disks: {len(mouse_disks)}", WHITE, font_size=14)

            if time.time() - last_mouse_click < 1.0:
                draw_text(anim, (20, 260), "Mouse clicked!", GREEN, font_size=16)
