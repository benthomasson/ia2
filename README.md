# ia2 — Interactive Animation v2

A Python library for creating 2D graphics, animations, and interactive visualizations. Refactored from the [ia](../interactive_animation) library with a cleaner, modular API.

## Install

```bash
# Using uv (preferred)
uv pip install -e .

# Or using pip
pip install -e .
```

### Run examples

Each example has [PEP 723](https://peps.python.org/pep-0723/) inline script metadata, so you can run any example directly with `uv run` — no manual install needed:

```bash
uv run examples/static_image.py
uv run examples/sine_wave.py
uv run examples/interactive_app.py
```

### System dependencies

- **cairo** — `brew install cairo` (macOS) or `sudo apt-get install libcairo2-dev` (Linux)
- **ffmpeg** — `brew install ffmpeg` (macOS) or `sudo apt-get install ffmpeg` (Linux)

### Python dependencies

Declared in `pyproject.toml` and installed automatically:

- `pycairo`
- `pygame-ce`
- `numpy`
- `scipy`
- `moderngl` (optional, for OpenGL rendering)

## Quick start

```python
from ia2.context import png
from ia2.draw import draw_circle, paint_background
from ia2.math import RED, WHITE

with png("output.png", size=(640, 480)) as img:
    paint_background(img, WHITE)
    draw_circle(img, (320, 240), 100, RED, width=5)
```

```python
from ia2.context import ffmpeg_wav
from ia2.frames import frames
from ia2.draw import draw_disk
from ia2.math import BLUE, BLACK, interpolate

with ffmpeg_wav("output.mp4", fps=60, size=(640, 480), length=3) as anim:
    x_values = interpolate(100, 540, 3 * 60)
    for frame in frames(anim, 3):
        draw_disk(anim, (x_values[frame], 240), 40, BLUE)
```

## Modules

| Module | Purpose |
|---|---|
| `ia2.context` | Context managers: `ffmpeg_wav`, `png`, `pygame_interactive`, `opengl_interactive` |
| `ia2.frames` | Frame loops: `frames`, `one_frame`, `wait`, `save_frame`, render helpers |
| `ia2.draw` | Drawing primitives: shapes, text, gradients, paths, construction helpers |
| `ia2.math` | Geometry, interpolation, coordinate conversions, color constants |
| `ia2.intersect` | Circle-circle, line-line, line-circle intersections |
| `ia2.audio` | WAV output, sample loading/mixing/playback, reverb |
| `ia2.bezier` | Bezier curves, paths, Coons patch shading, clipping |
| `ia2.scene` | Point transformations, z-ordering, 3D view ordering |
| `ia2.types` | Context classes: `Animation`, `Image`, `Interactive`, `Element`, `Scene` |
| `ia2.wave_table` | Wavetable synthesis, waveform generators, note frequencies |
