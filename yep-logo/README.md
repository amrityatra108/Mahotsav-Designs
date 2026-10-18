# yep logo: vector rebuild

The original `source/original.webp` (1121×1403 raster) was traced into clean vector outlines.
The SVG matches the original at 99.5% ink overlap, and it scales to any size without losing quality.

| File | Use |
| --- | --- |
| `yep-logo.svg` | Master vector: black, transparent, cropped to the artwork |
| `yep-logo-white.svg` | White version for dark backgrounds |
| `yep-logo-canvas.svg` | Original 1121×1403 composition on white |
| `png/yep-logo-8000w.png` | 8000×4547 transparent PNG |
| `png/yep-logo-white-8000w.png` | 8000×4547 transparent PNG, white ink |
| `png/yep-logo-canvas-8x.png` | 8968×11224 original layout on white (8×) |

To regenerate, or to export another size, change `PNG_WIDTH` in `build.py`:

    pip install potracer resvg-py opencv-python pillow numpy
    python build.py
