"""
Frame loop utilities: frame generators, save/display, render helpers.

Consolidated: frames2 → frames (the standard frame loop everyone uses).
"""

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Callable, List

import numpy as np
import pygame

from ia2.draw import draw_text, paint_background
from ia2.math import RED
from ia2.types import (
    Animation,
    AnimationSequence,
    Interactive,
    InteractiveAnimation,
    OpenGLInteractive,
    OpenGLInteractiveAnimation,
)


class StopAnimation(Exception):
    pass


class StopInteractive(Exception):
    pass


def frames(anim, time, bg_color=(0, 0, 0)):
    """Generate frames for a given duration with background paint and frame save.

    This is the standard frame loop. Each iteration paints the background,
    yields the frame number, then saves the frame.

    Example:
        for frame in frames(anim, 2.0):
            draw_circle(anim, (100, 100), 50, RED)
    """
    for frame in range(int(time * anim.fps)):
        anim.ctx.save()
        paint_background(anim, bg_color)
        yield frame
        anim.ctx.restore()
        save_frame(anim)


def one_frame(anim, bg_color=(0, 0, 0)):
    """Generate a single frame with background paint and frame save.

    Example:
        for frame in one_frame(anim):
            draw_circle(anim, (100, 100), 50, RED)
    """
    for frame in range(1):
        anim.ctx.save()
        paint_background(anim, bg_color)
        yield frame
        anim.ctx.restore()
        save_frame(anim)


@contextmanager
def one_frame2(anim, bg_color=(0, 0, 0)):
    """Context manager for a single frame.

    Example:
        with one_frame2(anim):
            draw_circle(anim, (100, 100), 50, RED)
    """
    anim.ctx.save()
    paint_background(anim, bg_color)
    yield
    anim.ctx.restore()
    save_frame(anim)


def wait(anim, seconds):
    """Wait for a specified number of seconds by writing frames or sleeping."""
    if isinstance(anim, (Animation, AnimationSequence)):
        for i in range(int(seconds * anim.fps)):
            anim.pipe.write(anim.surface.get_data())
        return int(seconds * anim.fps)
    elif isinstance(anim, Interactive):
        time.sleep(seconds)
    elif isinstance(anim, InteractiveAnimation):
        for i in range(int(seconds * anim.fps)):
            anim.pipe.write(anim.surface.get_data())
        time.sleep(seconds)


def save_frame(anim):
    """Save the current frame to the appropriate output (video, display, or OpenGL)."""

    def write_frame():
        data = anim.surface.get_data()
        anim.pipe.write(data)

    def display_frame():
        anim.clock_dt = anim.clock.tick(anim.fps) / 1000
        if anim.debug:
            draw_text(
                anim,
                (anim.width - 400, 100),
                f"FPS: {(1.0 / anim.clock_dt):.2f}",
                RED,
                "anonymous pro bold",
                50,
            )
        pygame_surface = pygame.image.frombuffer(
            anim.surface.get_data(), (anim.width, anim.height), "BGRA"
        )
        anim.display.blit(pygame_surface, (0, 0))
        pygame.display.flip()

        anim.events.extend([e for e in pygame.event.get()])
        events = [e.type for e in anim.events]
        if pygame.QUIT in events:
            raise StopInteractive()

    def display_frame_opengl():
        anim.clock_dt = anim.clock.tick(anim.fps)
        if anim.debug and anim.clock_dt > 0:
            fps_value = 1000.0 / anim.clock_dt
            draw_text(
                anim,
                (anim.width - 400, 100),
                f"FPS: {fps_value:.2f}",
                RED,
                "anonymous pro bold",
                50,
            )

        surface_data = anim.surface.get_data()
        data_array = np.frombuffer(surface_data, dtype=np.uint8)
        data_array = data_array.reshape((anim.height, anim.width, 4))
        rgba_array = data_array.copy()
        rgba_array[:, :, [0, 2]] = rgba_array[:, :, [2, 0]]

        anim.color_texture.write(rgba_array.tobytes())

        anim.gl_ctx.screen.use()
        anim.gl_ctx.clear(0.0, 0.0, 0.0, 1.0)
        anim.color_texture.use(0)
        anim.vao.render()

        anim.window.swap_buffers()

        events = anim.window.process_events()
        if anim.window.is_closing:
            raise StopInteractive()

    if isinstance(anim, (Animation, AnimationSequence)):
        write_frame()
    elif isinstance(anim, Interactive):
        display_frame()
    elif isinstance(anim, InteractiveAnimation):
        display_frame()
        write_frame()
    elif isinstance(anim, OpenGLInteractive):
        display_frame_opengl()
    elif isinstance(anim, OpenGLInteractiveAnimation):
        display_frame_opengl()
        write_frame()


def pause_frame(anim):
    """Display the current frame and wait for events (interactive only)."""
    pygame_surface = pygame.image.frombuffer(
        anim.surface.get_data(), (anim.width, anim.height), "BGRA"
    )
    anim.display.blit(pygame_surface, (0, 0))
    pygame.display.flip()

    anim.events.extend([e for e in pygame.event.get()])
    events = [e.type for e in anim.events]
    if pygame.QUIT in events:
        raise StopInteractive()


# --- Render helpers ---

def render_frames(anim, length, elements, bg_color=(0, 0, 0)):
    """Render a list of generator elements over a duration.

    Handles element lifecycle (StopIteration removes elements).
    Returns the final current_frame value.
    """
    start_frame = getattr(anim, 'current_frame', 0)
    for frame in frames(anim, length, bg_color):
        if hasattr(anim, 'current_frame'):
            anim.current_frame = frame + start_frame
        removed = []
        for element in elements:
            try:
                next(element)
            except StopIteration:
                removed.append(element)
            except TypeError:
                print("TypeError", element)
                raise
        for element in removed:
            elements.remove(element)
    if hasattr(anim, 'current_frame'):
        anim.current_frame += 1
        return anim.current_frame
    return 0


def render_image(img, elements, bg_color=(0, 0, 0)):
    """Render one frame of generator elements for a static image."""
    for frame in one_frame(img, bg_color):
        removed = []
        for element in elements:
            try:
                next(element)
            except StopIteration:
                removed.append(element)
            except TypeError:
                print("TypeError", element)
                raise
        for element in removed:
            elements.remove(element)
    return 0


def render_elements(anim, length, elements):
    """Render elements over a duration, yielding (frame, removed) each frame."""
    for frame in range(max(int(length * anim.fps), 1)):
        removed = []
        for element in elements:
            try:
                next(element)
            except StopIteration:
                removed.append(element)
            except BaseException:
                print(f"Error rendering {element}")
                raise
        for element in removed:
            elements.remove(element)
        yield frame, removed


def render_elements2(anim, length, *element_lists):
    """Render multiple element lists over a duration, yielding frame each frame."""
    for frame in range(max(int(length * anim.fps), 1)):
        for elements in element_lists:
            removed = []
            for i, element in enumerate(elements):
                if element is None:
                    continue
                try:
                    next(element)
                except StopIteration:
                    removed.append(i)
            for i in removed:
                elements[i] = None
        yield frame


def render_elements_once(anim, *element_lists):
    """Render multiple element lists for a single frame."""
    for elements in element_lists:
        removed = []
        for i, element in enumerate(elements):
            if element is None:
                continue
            try:
                next(element)
            except StopIteration:
                removed.append(i)
        for i in removed:
            elements[i] = None
