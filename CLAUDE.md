# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development

```bash
# Using uv (preferred)
uv pip install -e .

# Or using a virtualenv
source ~/venv/game/bin/activate
pip install -e .

# Run tests
python -m pytest tests/ -v

# Run an example standalone (uv resolves deps automatically via PEP 723)
uv run examples/static_image.py
```

The build backend is hatchling. Dependencies (pycairo, pygame-ce, numpy, scipy) are declared in `pyproject.toml`. All 8 examples have PEP 723 inline script metadata so they can be run standalone with `uv run`.

## Architecture

`ia2` is a Python library for creating 2D graphics, animations, and interactive visualizations. It was refactored from the `ia` package (in `~/git/interactive_animation`) following the plan in that repo's `REFACTORING_NOTES.md` — splitting a monolithic `ia.lang` module (~130 functions) into focused submodules.

### Module dependency graph

```
wave_table  types  math  intersect     (leaf modules — no internal deps)
    │         │      │       │
    │         │      ├───────┤
    │         │      │       │
    └────┬────┘      │       │
         │           │       │
       audio    draw─┘       │
         │       │           │
         │    bezier         │
         │       │           │
         └──frames           │
              │              │
           context       scene
```

### Key modules

- **types.py** — Data-holder classes (`Animation`, `Image`, `Interactive`, `AnimationSequence`, `Element`, `Scene`, etc.) that get passed to drawing/frame functions. These represent different rendering contexts (video, PNG, interactive pygame, OpenGL).
- **context.py** — Context managers that set up rendering: `ffmpeg_wav()`, `png()`, `pygame_interactive()`, `opengl_interactive()`. Also contains `FfmpegProxy` for video encoding with automatic part-splitting.
- **frames.py** — Frame loop generators: `frames()` (was `frames2` in v1) paints background, yields frame number, saves frame. Also `save_frame()`, `wait()`, and render helpers.
- **draw.py** — Cairo drawing primitives: shapes, text, gradients, paths, construction helpers. All take an `anim` context as first arg.
- **math.py** — Geometry (angle, distance, midpoint), interpolation (linear/sinusoidal), coordinate conversions, color constants (RED, BLUE, etc.), and closest-point-on-curve functions.
- **intersect.py** — Circle-circle, line-line, line-circle intersection functions.
- **audio.py** — WAV context manager, sample loading/mixing/playback, reverb, beat-synced mixing (`on_sixteenths`).
- **bezier.py** — Cubic Bezier drawing, connected Bezier paths, Coons patch shading, clipping.
- **scene.py** — Point transformation wrappers (`ScaledPoint`, `DeltaPoint`), z-ordering lists for 3D rendering, `JoinedLists`, `Ref`/`Value` helpers.
- **wave_table.py** — Wavetable synthesis: waveform generators (sawtooth, square, triangle), note frequency table, `fade_in_out`.

### Design patterns

- **Generator-based elements**: Animation elements are Python generators that yield each frame, allowing stateful animation with clean lifecycle management.
- **Context managers**: All rendering backends use `with` blocks for resource setup/teardown.
- **First-arg context**: Drawing functions take an `anim` context object as the first argument (carries cairo context, surface, dimensions, debug flags).
- **Construction mode**: Drawing functions like `draw_construction_line` only render when `anim.construct is True`.

### Refactoring decisions from v1

Numbered variants were consolidated: `frames2`→`frames`, `draw_points`+`draw_points2`→single `draw_points` (pass list for variable widths). Dropped one-off utilities: `noop`, `draw_number_line`, `make_icon`, `dict_value`, `scene_scale`, etc. Dropped redundant signatures: `draw_line2`, `draw_arc2/3/4`, `draw_vector2`.

### Angle convention

All angles in radians, standard math convention (0 = right, pi/2 = down in screen coords). Cairo uses a y-axis-down coordinate system.
