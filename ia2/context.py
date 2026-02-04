"""Context managers: ffmpeg, ffmpeg_wav, png, pygame_display, pygame_interactive, opengl_interactive."""

import os
import subprocess
import time
from contextlib import contextmanager

import cairo
import numpy as np
import pygame
from scipy.io import wavfile

from ia2.audio import combine
from ia2.draw import make_surface
from ia2.frames import StopAnimation, StopInteractive
from ia2.types import (
    Animation,
    AnimationSequence,
    Image,
    Interactive,
    InteractiveAnimation,
    OpenGLInteractive,
    OpenGLInteractiveAnimation,
)
from ia2.wave_table import fade_in_out


class FfmpegProxy:
    """Proxy for managing FFmpeg video encoding, with automatic part splitting."""

    def __init__(self, filename, width, height, fps):
        self.final_filename = filename
        self.base, self.ext = os.path.splitext(filename)
        self.part_number = 0
        self.width = width
        self.height = height
        self.fps = fps
        self.writing_process = None
        self.max_frames = 60 * 60
        self.frame_count = 0
        self.parts = []

    def start_process(self):
        self.filename = f"{self.base}.{self.part_number:04d}{self.ext}"
        self.parts.append(self.filename)
        self.part_number += 1
        command = (
            f"ffmpeg -y -f rawvideo -vcodec rawvideo "
            f"-s {self.width}x{self.height} -pix_fmt bgra -r {self.fps} -i - "
            f"-threads 0 -preset fast -an -vcodec libx264 -crf 17 "
            f"-pix_fmt yuv420p -f mp4 {self.filename}"
        )
        command = command.split(" ")
        self.writing_process = subprocess.Popen(
            command, stdin=subprocess.PIPE, stderr=subprocess.PIPE
        )
        self.frame_count = 0

    def stop_process(self):
        if self.writing_process is not None:
            self.writing_process.stdin.close()
            self.writing_process.wait()
            with open("ffmpeg.log", "a") as f:
                f.write(self.writing_process.stderr.read().decode("utf-8"))
            self.writing_process = None

    def write(self, data):
        self.frame_count += 1
        if self.frame_count > self.max_frames:
            self.stop_process()
            self.start_process()
        if self.writing_process is None:
            self.start_process()
        self.writing_process.stdin.write(data)

    def combine_parts(self):
        if len(self.parts) == 0:
            print("No parts to combine")
            return
        elif len(self.parts) == 1:
            os.rename(self.filename, self.final_filename)
        else:
            with open("files.txt", "w") as f:
                for part in self.parts:
                    f.write(f"file '{part}'\n")
            command = f"ffmpeg -y -f concat -safe 0 -i files.txt -c copy {self.final_filename}"
            command = command.split(" ")
            subprocess.run(command)


@contextmanager
def ffmpeg(filename="output.mp4", fps=30, size=(640, 480)):
    """Context manager for creating H.264 video output using FFmpeg."""
    proxy = FfmpegProxy(filename, size[0], size[1], fps)
    try:
        yield proxy
    except StopAnimation:
        print("Stopping animation")
    finally:
        proxy.stop_process()
        proxy.combine_parts()


@contextmanager
def ffmpeg_wav(
    video_file_name="output_video.mp4",
    audio_file_name="output_audio.wav",
    combined_file_name="output.mp4",
    fps=60,
    size=(640, 480),
    tempo=120,
    sample_rate=44100,
    length=60,
    debug=False,
):
    """Context manager for creating synchronized video and audio output."""
    if os.path.exists(video_file_name):
        os.unlink(video_file_name)
    if os.path.exists(audio_file_name):
        os.unlink(audio_file_name)
    start = time.time()
    surface, ctx = make_surface(*size)
    proxy = FfmpegProxy(video_file_name, size[0], size[1], fps)
    data = np.zeros((int(sample_rate * (length + 3))), dtype=np.float32)
    anim = AnimationSequence(
        ctx, surface, proxy, size[0], size[1], fps,
        data, tempo, sample_rate, length, debug,
    )
    try:
        yield anim
    except StopAnimation:
        print("Stopping animation")
    finally:
        proxy.stop_process()
        proxy.combine_parts()

        max_val = np.max(np.abs(data), axis=0)
        if max_val != 0:
            data /= max_val
        data = fade_in_out(data)
        wavfile.write(audio_file_name, sample_rate, data)

        if os.path.exists(video_file_name) and os.path.exists(audio_file_name):
            combine(video_file_name, audio_file_name, combined_file_name)
        elif os.path.exists(video_file_name):
            print("Missing video")
        elif os.path.exists(audio_file_name):
            print("Missing audio")
        end = time.time()
        print(f"Total time: {end - start}")


@contextmanager
def png(filename="output.png", size=(640, 480), debug=False):
    """Context manager for creating static PNG image output."""
    surface, ctx = make_surface(*size)
    img = Image(ctx, surface, size[0], size[1], debug)
    try:
        yield img
    finally:
        surface.write_to_png(filename)


@contextmanager
def pygame_display(size=(640, 480), icon=None, title=None):
    """Context manager for creating a PyGame display window."""
    width, height = size
    pygame.init()
    pygame.mouse.set_visible(False)
    if icon is not None:
        pygame.display.set_icon(icon)
    if title is not None:
        pygame.display.set_caption(title)
    screen = pygame.display.set_mode((width, height), 0, 32)
    try:
        yield screen
    except StopInteractive:
        print("Stopping interactive")
    finally:
        pygame.quit()


@contextmanager
def pygame_interactive(
    fps=60,
    size=(640, 480),
    debug=False,
    events=[],
    commands=[],
    icon=None,
    title=None,
    video_output=None,
    wav_output=None,
    tempo=60,
    rate=44100,
    length=60,
    video_file_name="output_video.mp4",
    audio_file_name="output_audio.wav",
):
    """Context manager for an interactive PyGame window with optional recording."""
    width, height = size
    start = time.time()
    pygame.init()
    pygame.mouse.set_visible(False)
    if icon is not None:
        pygame.display.set_icon(icon)
    if title is not None:
        pygame.display.set_caption(title)
    display = pygame.display.set_mode((width, height), 0, 32)
    surface, context = make_surface(width, height)
    clock = pygame.time.Clock()
    proxy = None
    data = None
    if video_output is not None:
        proxy = FfmpegProxy(video_file_name, size[0], size[1], fps)
        data = np.zeros((int(rate * (length + 3))), dtype=np.float32)
        anim = InteractiveAnimation(
            context, surface, proxy, display, clock, events, commands,
            fps, width, height, debug,
            tempo=tempo, length=length, rate=rate, wav_file=data,
        )
    else:
        anim = Interactive(
            context, surface, display, clock, events, commands,
            fps, width, height, debug,
        )
    try:
        yield anim
    except StopInteractive:
        print("Stopping interactive")
    finally:
        pygame.quit()
        if proxy:
            proxy.stop_process()
            proxy.combine_parts()

        if data is not None:
            max_val = np.max(np.abs(data), axis=0)
            if max_val != 0:
                data /= max_val
            data = fade_in_out(data)
            wavfile.write(audio_file_name, rate, data)

        if video_output is not None:
            if os.path.exists(video_file_name) and os.path.exists(audio_file_name):
                combine(video_file_name, audio_file_name, video_output)
            elif os.path.exists(video_file_name):
                print("Missing video")
            elif os.path.exists(audio_file_name):
                print("Missing audio")
            end = time.time()
            print(f"Total time: {end - start}")


@contextmanager
def opengl_interactive(
    fps=60,
    size=(640, 480),
    debug=False,
    events=[],
    commands=[],
    icon=None,
    title=None,
    video_output=None,
    wav_output=None,
    tempo=60,
    rate=44100,
    length=60,
    video_file_name="output_video.mp4",
    audio_file_name="output_audio.wav",
):
    """Context manager for an interactive OpenGL window with moderngl support."""
    try:
        import moderngl
    except ImportError:
        raise ImportError(
            "moderngl is required for OpenGL support. Install with: pip install moderngl"
        )

    width, height = size
    start = time.time()

    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
    )
    pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
    pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

    pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF)
    if title:
        pygame.display.set_caption(title)

    ctx = moderngl.create_context()

    class MockWindow:
        def __init__(self, size, events_list):
            self.size = size
            self.is_closing = False
            self.events_list = events_list

        def swap_buffers(self):
            pygame.display.flip()

        def process_events(self):
            evts = pygame.event.get()
            self.events_list.extend(evts)
            for event in evts:
                if event.type == pygame.QUIT:
                    self.is_closing = True
            return evts

        def close(self):
            self.is_closing = True

    window = MockWindow(size, events)

    color_texture = ctx.texture(size, 4)
    depth_texture = ctx.depth_texture(size)
    fbo = ctx.framebuffer(
        color_attachments=[color_texture], depth_attachment=depth_texture
    )

    cairo_surface, cairo_context = make_surface(width, height)

    vertices = np.array([
        -1.0, -1.0, 0.0, 1.0,
         1.0, -1.0, 1.0, 1.0,
         1.0,  1.0, 1.0, 0.0,
        -1.0,  1.0, 0.0, 0.0,
    ], dtype=np.float32)

    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    vbo = ctx.buffer(vertices.tobytes())
    ibo = ctx.buffer(indices.tobytes())
    vao = ctx.vertex_array(
        ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_position;
            in vec2 in_texcoord;
            out vec2 v_texcoord;
            void main() {
                gl_Position = vec4(in_position, 0.0, 1.0);
                v_texcoord = in_texcoord;
            }
            """,
            fragment_shader="""
            #version 330
            uniform sampler2D u_texture;
            in vec2 v_texcoord;
            out vec4 fragColor;
            void main() {
                fragColor = texture(u_texture, v_texcoord);
            }
            """,
        ),
        [(vbo, '2f 2f', 'in_position', 'in_texcoord')],
        ibo,
    )

    class MockClock:
        def __init__(self):
            self.last_time = time.time()

        def tick(self, fps):
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = time.time()
            return int(dt * 1000)

    clock = MockClock()

    proxy = None
    data = None
    if video_output is not None:
        proxy = FfmpegProxy(video_file_name, size[0], size[1], fps)
        data = np.zeros((int(rate * (length + 3))), dtype=np.float32)
        anim = OpenGLInteractiveAnimation(
            cairo_context, cairo_surface, proxy, window, ctx, fbo,
            color_texture, vao, clock, events, commands,
            fps, width, height, debug,
            tempo=tempo, length=length, rate=rate, wav_file=data,
        )
    else:
        anim = OpenGLInteractive(
            cairo_context, cairo_surface, window, ctx, fbo,
            color_texture, vao, clock, events, commands,
            fps, width, height, debug,
        )

    try:
        yield anim
    except StopInteractive:
        print("Stopping OpenGL interactive")
    finally:
        window.close()
        if proxy:
            proxy.stop_process()
            proxy.combine_parts()

        if data is not None:
            max_val = np.max(np.abs(data), axis=0)
            if max_val != 0:
                data /= max_val
            data = fade_in_out(data)
            wavfile.write(audio_file_name, rate, data)

        if video_output is not None:
            if os.path.exists(video_file_name) and os.path.exists(audio_file_name):
                combine(video_file_name, audio_file_name, video_output)
            elif os.path.exists(video_file_name):
                print("Missing video")
            elif os.path.exists(audio_file_name):
                print("Missing audio")
            end = time.time()
            print(f"Total time: {end - start}")
