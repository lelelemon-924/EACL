#!/usr/bin/env python3

"""Repair the over-tight crop in the draw.io PDF exports.

    python3 scripts/fix_figure_bbox.py IN.pdf OUT.pdf [--pad PT]

The exports in figures/final2/ carry a clip rectangle that is inset from their
own MediaBox, and the artwork runs past it: in fig2_pipeline the clip ends at
x = 1133.25 pt while panel 4's box and the grey zone border sit at x ~ 1153, so
their right and bottom edges are simply not painted. Scaling the figure down in
LaTeX cannot bring back strokes that were never drawn.

This releases that one clip and re-crops the page to what is actually painted,
so nothing is cut and the margins are even. Everything else is untouched.

Needs pikepdf and Ghostscript; the bounding box is measured by rendering,
because the drawing is deep inside nested transforms.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pikepdf

RENDER_DPI = 400
# The clip draw.io emits around the whole drawing, as opposed to the per-label
# overflow:hidden clips, which are small and must be left alone.
OUTER_CLIP = re.compile(rb"78\.125 [\d.]+ [\d.]+ [\d.]+ re(\s*\n?W\* n)")
RELEASED = b"-99999 -99999 999999 999999 re"


def release_clip(pdf):
    page = pdf.pages[0]
    data = page.obj["/Contents"].read_bytes()
    patched, count = OUTER_CLIP.subn(RELEASED + rb"\1", data)
    if count:
        page.Contents = pdf.make_stream(patched)
    return count


def painted_bbox(pdf_path, media):
    """Content bbox in PDF points, measured from a render of `media`."""
    from PIL import Image
    import numpy as np

    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "probe.png"
        subprocess.run(
            ["gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=png16m", f"-r{RENDER_DPI}",
             f"-sOutputFile={png}", str(pdf_path)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        ink = np.array(Image.open(png).convert("L")) < 250

    rows = np.where(ink.any(axis=1))[0]
    cols = np.where(ink.any(axis=0))[0]
    if not len(rows):
        raise SystemExit(f"{pdf_path}: rendered blank")
    scale = 72 / RENDER_DPI
    x0, y0, x1, y1 = media
    return (float(x0 + cols[0] * scale), float(y1 - rows[-1] * scale),
            float(x0 + cols[-1] * scale), float(y1 - rows[0] * scale))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--pad", type=float, default=2.0, help="margin in points")
    args = ap.parse_args()

    pdf = pikepdf.open(args.input)
    original = [float(v) for v in pdf.pages[0].MediaBox]

    released = release_clip(pdf)
    # Probe on a page large enough that the released artwork cannot hit an edge.
    probe_media = [original[0] - 200, original[1] - 200,
                   original[2] + 200, original[3] + 200]
    pdf.pages[0].MediaBox = probe_media
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "probe.pdf"
        pdf.save(probe)
        bbox = painted_bbox(probe, probe_media)

    out = pikepdf.open(args.input)
    release_clip(out)
    media = [bbox[0] - args.pad, bbox[1] - args.pad,
             bbox[2] + args.pad, bbox[3] + args.pad]
    out.pages[0].MediaBox = media
    out.save(args.output)

    cut = [
        name for name, gap in (
            ("left", original[0] - bbox[0]), ("bottom", original[1] - bbox[1]),
            ("right", bbox[2] - original[2]), ("top", bbox[3] - original[3]),
        ) if gap > 0.25
    ]
    print(f"{Path(args.input).name}: released {released} clip op(s)")
    print(f"  painted bbox   {bbox[0]:.2f} {bbox[1]:.2f} {bbox[2]:.2f} {bbox[3]:.2f}")
    print(f"  old MediaBox   {original[0]:.2f} {original[1]:.2f} "
          f"{original[2]:.2f} {original[3]:.2f}")
    print(f"  new MediaBox   {media[0]:.2f} {media[1]:.2f} {media[2]:.2f} {media[3]:.2f}")
    print(f"  size {media[2]-media[0]:.2f} x {media[3]-media[1]:.2f} pt, "
          f"aspect {(media[2]-media[0])/(media[3]-media[1]):.4f}")
    print(f"  artwork was cut off at: {', '.join(cut) if cut else 'nowhere'}")


if __name__ == "__main__":
    sys.exit(main())
