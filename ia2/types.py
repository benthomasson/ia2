from __future__ import annotations

from typing import Any, Callable, Generator, Optional, Union

import cairo
import numpy as np
import pygame


class Animation:
    """Video animation context with FFmpeg pipe for frame-by-frame encoding."""

    __slots__ = [
        "ctx", "surface", "pipe", "fps", "width", "height",
        "debug", "debug_color", "construct", "selected", "ui_scale",
    ]

    def __init__(
        self,
        ctx: cairo.Context,
        surface: cairo.Surface,
        pipe: Any,
        fps: int,
        width: int,
        height: int,
        debug: bool = False,
        debug_color: tuple[float, float, float] = (1, 0, 0),
        construct: bool = False,
        selected: bool = False,
        ui_scale: float = 1,
    ) -> None:
        self.ctx = ctx
        self.surface = surface
        self.pipe = pipe
        self.fps = fps
        self.width = width
        self.height = height
        self.debug = debug
        self.debug_color = debug_color
        self.construct = construct
        self.selected = selected
        self.ui_scale = ui_scale


class Image:
    """Static PNG image rendering context."""

    __slots__ = [
        "ctx", "surface", "width", "height", "debug", "fps",
        "construct", "selected", "debug_color", "ui_scale",
    ]

    def __init__(
        self,
        ctx: cairo.Context,
        surface: cairo.Surface,
        width: int,
        height: int,
        debug: bool = False,
        construct: bool = False,
        debug_color: tuple[float, float, float] = (1, 0, 0),
        selected: bool = False,
        ui_scale: float = 1,
    ) -> None:
        self.ctx = ctx
        self.surface = surface
        self.width = width
        self.height = height
        self.debug = debug
        self.fps = 1
        self.construct = construct
        self.debug_color = debug_color
        self.selected = selected
        self.ui_scale = ui_scale


class Sequence:
    """Audio-only sequence context with tempo and sample rate."""

    __slots__ = ["wav_file", "tempo", "rate", "fps", "current_frame", "debug"]

    def __init__(
        self, wav_file: np.ndarray, tempo: int, rate: int, fps: int, debug: bool = False
    ) -> None:
        self.wav_file = wav_file
        self.tempo = tempo
        self.rate = rate
        self.fps = fps
        self.current_frame = 0
        self.debug = debug


class AnimationSequence:
    """Combined video and audio rendering context with beat-synced timing."""

    __slots__ = [
        "ctx", "surface", "pipe", "width", "height", "fps",
        "wav_file", "tempo", "rate", "length", "current_frame",
        "debug", "debug_color", "construct", "selected", "ui_scale",
    ]

    def __init__(
        self,
        ctx: cairo.Context,
        surface: cairo.Surface,
        pipe: Any,
        width: int,
        height: int,
        fps: int,
        wav_file: np.ndarray,
        tempo: int,
        rate: int,
        length: int,
        debug: bool = False,
        debug_color: tuple[float, float, float] = (1, 0, 0),
        construct: bool = False,
        selected: bool = False,
        ui_scale: float = 1,
    ) -> None:
        self.ctx = ctx
        self.surface = surface
        self.pipe = pipe
        self.width = width
        self.height = height
        self.fps = fps
        self.wav_file = wav_file
        self.tempo = tempo
        self.rate = rate
        self.length = length
        self.current_frame = 0
        self.debug = debug
        self.debug_color = debug_color
        self.construct = construct
        self.selected = selected
        self.ui_scale = ui_scale

    @property
    def beat(self) -> float:
        return 60 / self.tempo

    @property
    def whole(self) -> float:
        return self.beat * 4

    @property
    def half(self) -> float:
        return self.beat * 2

    @property
    def quarter(self) -> float:
        return self.beat

    @property
    def eighth(self) -> float:
        return self.beat / 2

    @property
    def sixteenth(self) -> float:
        return self.beat / 4


class Interactive:
    """PyGame interactive display context with event handling."""

    __slots__ = [
        "ctx", "surface", "display", "clock", "events", "commands",
        "fps", "width", "height", "debug", "debug_color",
        "construct", "selected", "ui_scale", "clock_dt",
    ]

    def __init__(
        self,
        ctx: cairo.Context,
        surface: cairo.Surface,
        display: pygame.Surface,
        clock: pygame.time.Clock,
        events: list[pygame.event.Event],
        commands: list[Callable],
        fps: int,
        width: int,
        height: int,
        debug: bool = False,
        debug_color: tuple[float, float, float] = (1, 0, 0),
        construct: bool = False,
        selected: bool = False,
        ui_scale: float = 1,
        clock_dt: Optional[float] = None,
    ) -> None:
        self.ctx = ctx
        self.surface = surface
        self.display = display
        self.clock = clock
        self.events = events
        self.commands = commands
        self.fps = fps
        self.width = width
        self.height = height
        self.debug = debug
        self.debug_color = debug_color
        self.construct = construct
        self.selected = selected
        self.ui_scale = ui_scale
        self.clock_dt = clock_dt


class InteractiveAnimation:
    """PyGame interactive context with simultaneous video/audio recording."""

    __slots__ = [
        "ctx", "surface", "pipe", "display", "clock", "events", "commands",
        "fps", "width", "height", "debug", "debug_color",
        "construct", "selected", "ui_scale", "clock_dt",
        "wav_file", "tempo", "rate", "current_frame", "length",
    ]

    def __init__(
        self,
        ctx: cairo.Context,
        surface: cairo.Surface,
        pipe: Any,
        display: pygame.Surface,
        clock: pygame.time.Clock,
        events: list[pygame.event.Event],
        commands: list[Callable],
        fps: int,
        width: int,
        height: int,
        debug: bool = False,
        debug_color: tuple[float, float, float] = (1, 0, 0),
        construct: bool = False,
        selected: bool = False,
        ui_scale: float = 1,
        clock_dt: Optional[float] = None,
        wav_file: Optional[np.ndarray] = None,
        tempo: int = 120,
        rate: int = 44100,
        current_frame: int = 0,
        length: int = 60,
    ) -> None:
        self.ctx = ctx
        self.surface = surface
        self.pipe = pipe
        self.display = display
        self.clock = clock
        self.events = events
        self.commands = commands
        self.fps = fps
        self.width = width
        self.height = height
        self.debug = debug
        self.debug_color = debug_color
        self.construct = construct
        self.selected = selected
        self.ui_scale = ui_scale
        self.clock_dt = clock_dt
        self.current_frame = current_frame
        self.rate = rate
        self.tempo = tempo
        self.wav_file = wav_file
        self.length = length

    @property
    def beat(self) -> float:
        return 60 / self.tempo

    @property
    def whole(self) -> float:
        return self.beat * 4

    @property
    def half(self) -> float:
        return self.beat * 2

    @property
    def quarter(self) -> float:
        return self.beat

    @property
    def eighth(self) -> float:
        return self.beat / 2

    @property
    def sixteenth(self) -> float:
        return self.beat / 4


class OpenGLInteractive:
    """OpenGL interactive display context using moderngl and PyGame."""

    __slots__ = [
        "ctx", "surface", "window", "gl_ctx", "fbo", "color_texture", "vao",
        "clock", "events", "commands", "fps", "width", "height",
        "debug", "debug_color", "construct", "selected", "ui_scale", "clock_dt",
    ]

    def __init__(
        self,
        ctx: cairo.Context,
        surface: cairo.Surface,
        window: Any,
        gl_ctx: Any,
        fbo: Any,
        color_texture: Any,
        vao: Any,
        clock: Any,
        events: list,
        commands: list[Callable],
        fps: int,
        width: int,
        height: int,
        debug: bool = False,
        debug_color: tuple[float, float, float] = (1, 0, 0),
        construct: bool = False,
        selected: bool = False,
        ui_scale: float = 1,
        clock_dt: Optional[float] = None,
    ) -> None:
        self.ctx = ctx
        self.surface = surface
        self.window = window
        self.gl_ctx = gl_ctx
        self.fbo = fbo
        self.color_texture = color_texture
        self.vao = vao
        self.clock = clock
        self.events = events
        self.commands = commands
        self.fps = fps
        self.width = width
        self.height = height
        self.debug = debug
        self.debug_color = debug_color
        self.construct = construct
        self.selected = selected
        self.ui_scale = ui_scale
        self.clock_dt = clock_dt


class OpenGLInteractiveAnimation:
    """OpenGL interactive context with simultaneous video/audio recording."""

    __slots__ = [
        "ctx", "surface", "pipe", "window", "gl_ctx", "fbo", "color_texture", "vao",
        "clock", "events", "commands", "fps", "width", "height",
        "debug", "debug_color", "construct", "selected", "ui_scale", "clock_dt",
        "wav_file", "tempo", "rate", "current_frame", "length",
    ]

    def __init__(
        self,
        ctx: cairo.Context,
        surface: cairo.Surface,
        pipe: Any,
        window: Any,
        gl_ctx: Any,
        fbo: Any,
        color_texture: Any,
        vao: Any,
        clock: Any,
        events: list,
        commands: list[Callable],
        fps: int,
        width: int,
        height: int,
        debug: bool = False,
        debug_color: tuple[float, float, float] = (1, 0, 0),
        construct: bool = False,
        selected: bool = False,
        ui_scale: float = 1,
        clock_dt: Optional[float] = None,
        wav_file: Optional[np.ndarray] = None,
        tempo: int = 120,
        rate: int = 44100,
        current_frame: int = 0,
        length: int = 60,
    ) -> None:
        self.ctx = ctx
        self.surface = surface
        self.pipe = pipe
        self.window = window
        self.gl_ctx = gl_ctx
        self.fbo = fbo
        self.color_texture = color_texture
        self.vao = vao
        self.clock = clock
        self.events = events
        self.commands = commands
        self.fps = fps
        self.width = width
        self.height = height
        self.debug = debug
        self.debug_color = debug_color
        self.construct = construct
        self.selected = selected
        self.ui_scale = ui_scale
        self.clock_dt = clock_dt
        self.current_frame = current_frame
        self.rate = rate
        self.tempo = tempo
        self.wav_file = wav_file
        self.length = length

    @property
    def beat(self) -> float:
        return 60.0 / self.tempo

    @property
    def whole(self) -> float:
        return self.beat * 4

    @property
    def half(self) -> float:
        return self.beat * 2

    @property
    def quarter(self) -> float:
        return self.beat

    @property
    def eighth(self) -> float:
        return self.beat / 2

    @property
    def sixteenth(self) -> float:
        return self.beat / 4


class Element:
    """A named generator-based animation element with position and config state."""

    __slots__ = [
        "name", "generator", "visible", "point", "points",
        "scalefactor", "rotation", "config", "config_name",
        "control_points", "command", "command_kwargs", "command_points",
        "command_name", "command_type", "selected", "points3d",
        "config_ui_fn", "data",
    ]

    def __init__(
        self,
        name: str,
        generator: Generator,
        visible: bool = True,
        point: Optional[tuple[float, float]] = None,
        points: Optional[list[tuple[float, float]]] = None,
        scalefactor: Optional[float] = None,
        rotation: Optional[float] = None,
        config: Optional[dict[str, Any]] = None,
        config_name: Optional[str] = None,
        control_points: Optional[list[tuple[float, float]]] = None,
        command: Optional[Callable] = None,
        command_kwargs: Optional[dict[str, Any]] = None,
        command_points: Optional[list[tuple[float, float]]] = None,
        command_name: Optional[str] = None,
        command_type: Optional[str] = None,
        selected: bool = False,
        points3d: Optional[list[tuple[float, float, float]]] = None,
        config_ui_fn: Optional[Callable] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.generator = generator
        self.visible = visible
        self.point = point
        self.points = points if points is not None else []
        self.scalefactor = scalefactor
        self.rotation = rotation
        self.config = config
        self.config_name = config_name
        self.control_points = control_points if control_points is not None else []
        self.command = command
        self.command_kwargs = command_kwargs
        self.command_points = command_points
        self.command_name = command_name
        self.command_type = command_type
        self.selected = selected
        self.points3d = points3d
        self.config_ui_fn = config_ui_fn
        self.data = data

    def __iter__(self) -> Iterator[Union[str, Generator, bool]]:
        return iter([self.name, self.generator, self.visible])

    def __repr__(self) -> str:
        return f"Element({self.name}, {self.generator}, {self.visible})"

    def __getitem__(self, key: int) -> Union[str, Generator, bool]:
        if key == 0:
            return self.name
        elif key == 1:
            return self.generator
        elif key == 2:
            return self.visible
        else:
            raise IndexError("Index out of range")


class Scene(dict):
    """3D scene parameters: rotation angles, translation, scale, and projection settings."""

    def __init__(
        self,
        x_angle: float = 0,
        y_angle: float = 0,
        z_angle: float = 0,
        x_t: float = 0,
        y_t: float = 0,
        z_t: float = 0,
        scale: float = 1,
        p: tuple[float, float] = (0, 0),
        rotation_order: str = "xyz",
        focal_length: float = 1000,
        z_offset: float = 100,
        projection: str = "isometric",
    ) -> None:
        dict.__init__(
            self,
            x_angle=x_angle, y_angle=y_angle, z_angle=z_angle,
            x_t=x_t, y_t=y_t, z_t=z_t,
            scale=scale, p=p,
            rotation_order=rotation_order,
            focal_length=focal_length,
            z_offset=z_offset,
            projection=projection,
        )


class MemoryRange:
    """A named range within a MemoryMap, with size per item and item count."""

    __slots__ = ["name", "size", "n"]

    def __init__(self, name: str, size: int, n: int) -> None:
        self.name = name
        self.size = size
        self.n = n

    def __getitem__(self, i: int) -> Union[str, int]:
        if i == 0:
            return self.name
        elif i == 1:
            return self.size
        elif i == 2:
            return self.n
        else:
            raise IndexError()


class MemoryMap:
    """Contiguous memory layout of named ranges, providing slice access by name."""

    __slots__ = ["ranges", "indexes", "length"]

    def __init__(self, ranges: Optional[list[tuple[str, int, int]]] = None) -> None:
        if ranges is None:
            ranges = []
        self.ranges = ranges
        self.indexes: dict[str, list[int]] = {}

        current_loc = 0
        for i, (name, size, n) in enumerate(ranges):
            self.indexes[name] = [current_loc, size, n]
            current_loc += size * n
        self.length = current_loc

    def __len__(self) -> int:
        return self.length

    def slices(self, name: str) -> list[list[int]]:
        start, size, n = self.indexes[name]
        return [[start + (size * i), start + (size * (i + 1))] for i in range(n)]
