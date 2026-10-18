"""Rebuild the "yep" logo as vector art and export high-resolution PNGs.

The source raster is supersampled, smoothed and traced with potrace, so the
output is clean Bezier outlines rather than enlarged pixels. Every PNG is
rendered from the SVG, so any size can be produced without quality loss.

    pip install potracer resvg-py opencv-python pillow numpy
    python build.py source/original.webp
"""
import io
import sys
from pathlib import Path

import cv2
import numpy as np
import potrace
import resvg_py
from PIL import Image

HERE = Path(__file__).parent
SUPERSAMPLE = 4   # trace at 4x the source resolution for smoother curves
PAD = 40          # padding (source px) around the ink for the cropped logo
PNG_WIDTH = 8000  # width of the cropped PNG exports

Image.MAX_IMAGE_PIXELS = None  # the 8x canvas export is ~100 MP


def trace(src):
    gray = np.array(Image.open(src).convert("L")).astype(np.float32)
    h, w = gray.shape
    s = SUPERSAMPLE
    up = cv2.resize(gray, (w * s, h * s), interpolation=cv2.INTER_CUBIC)
    up = cv2.GaussianBlur(up, (0, 0), sigmaX=s * 0.6)
    ink = up < 128

    # potracer treats False as foreground, so pass the background mask
    plist = potrace.Bitmap(~ink).trace(
        turdsize=40 * s * s,
        turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
        alphamax=1.0,
        opticurve=True,
        opttolerance=0.2,
    )

    pt = lambda p: f"{p.x / s:.2f} {p.y / s:.2f}"
    d = []
    for curve in plist:
        d.append(f"M{pt(curve.start_point)}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{pt(seg.c)}L{pt(seg.end_point)}")
            else:
                d.append(f"C{pt(seg.c1)} {pt(seg.c2)} {pt(seg.end_point)}")
        d.append("Z")

    ys, xs = np.where(gray < 128)
    bbox = (xs.min() - PAD, ys.min() - PAD, xs.max() - xs.min() + 2 * PAD, ys.max() - ys.min() + 2 * PAD)
    return "".join(d), (w, h), bbox


def svg(d, viewbox, size, fill="#000", background=None):
    x, y, w, h = viewbox
    bg = f'\n  <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{background}"/>' if background else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}" '
        f'width="{size[0]}" height="{size[1]}">{bg}\n'
        f'  <path fill="{fill}" fill-rule="evenodd" d="{d}"/>\n</svg>\n'
    )


def render(svg_text, out, width):
    png = resvg_py.svg_to_bytes(svg_string=svg_text, width=width)
    Image.open(io.BytesIO(bytes(png))).save(out, optimize=True, dpi=(300, 300))
    print(f"  {out.relative_to(HERE)}  {Image.open(out).size}")


def main(src):
    d, (cw, ch), crop = trace(src)
    (HERE / "png").mkdir(exist_ok=True)

    logo = svg(d, crop, (crop[2], crop[3]))
    logo_white = svg(d, crop, (crop[2], crop[3]), fill="#fff")
    canvas = svg(d, (0, 0, cw, ch), (cw, ch), background="#fff")

    for name, text in [("yep-logo.svg", logo), ("yep-logo-white.svg", logo_white), ("yep-logo-canvas.svg", canvas)]:
        (HERE / name).write_text(text)
        print(f"  {name}")

    render(logo, HERE / "png" / f"yep-logo-{PNG_WIDTH}w.png", PNG_WIDTH)
    render(logo_white, HERE / "png" / f"yep-logo-white-{PNG_WIDTH}w.png", PNG_WIDTH)
    render(canvas, HERE / "png" / "yep-logo-canvas-8x.png", cw * 8)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else HERE / "source" / "original.webp")
