#!/usr/bin/env python3

"""Put the four panel boxes of Figure 2 on a common top and bottom edge.

    python3 scripts/align_fig2_panels.py IN.pdf OUT.pdf

The draw.io export gives each panel its own vertical extent — 46.5..366.0,
46.5..362.5, 48.5..364.5, 48.5..364.5 — so the row of four boxes is staggered by
up to 3.5 drawing units, about 1 pt once the figure is placed at \\textwidth.

The exporter writes these boxes as bezier subpaths in the drawing's own
coordinates, so they can be edited in place, which keeps the fonts and the rest
of the artwork byte-identical. Each box is a rounded rectangle: two corner arcs
joined by straight sides. Shifting every point above the box's vertical midpoint
by one delta and everything below it by another moves the two arcs rigidly and
just lengthens the straight sides, so the corner radius is preserved.

Run before scripts/fix_figure_bbox.py.
"""

import argparse
import re
import sys

import pikepdf

NUM = r"-?\d+(?:\.\d+)?"
SUBPATH = re.compile(rf"({NUM}) ({NUM}) m\n(.*?)\nh\n", re.S)
COORD = re.compile(rf"({NUM}) ({NUM})(?= [lcm]|\n[lc])")
# Operand counts for the path operators these subpaths use.
PAIRS = {"m": 1, "l": 1, "c": 3}


def points(segment):
    return [(float(m.group(1)), float(m.group(2))) for m in COORD.finditer(segment)]


def is_panel_box(segment):
    pts = points(segment)
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    box = (min(xs), min(ys), max(xs), max(ys))
    wide = box[2] - box[0] > 300
    tall = 300 < box[3] - box[1] < 340
    return box if wide and tall else None


def reposition(segment, top, bottom):
    """Move the subpath's top and bottom edges to `top` and `bottom`.

    Every number in one of these subpaths is a path coordinate and they strictly
    alternate x, y, so only the odd ones are rewritten and the surrounding
    whitespace is left exactly as the exporter wrote it — the script stays
    re-runnable against its own output.
    """
    ys = [p[1] for p in points(segment)]
    cur_top, cur_bottom = min(ys), max(ys)
    middle = (cur_top + cur_bottom) / 2
    dy_top, dy_bottom = top - cur_top, bottom - cur_bottom

    index = -1

    def rewrite(match):
        nonlocal index
        index += 1
        if index % 2 == 0:  # an x coordinate
            return match.group(0)
        y = float(match.group(0))
        return f"{y + (dy_top if y < middle else dy_bottom):.5f}".rstrip("0").rstrip(".")

    return re.sub(NUM, rewrite, segment)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--top", type=float, default=46.5)
    ap.add_argument("--bottom", type=float, default=366.0)
    args = ap.parse_args()

    pdf = pikepdf.open(args.input)
    data = pdf.pages[0].obj["/Contents"].read_bytes().decode("latin-1")

    found = [(m.start(), m.end(), box) for m in SUBPATH.finditer(data)
             if (box := is_panel_box(m.group(0)))]
    if not found:
        raise SystemExit("no panel boxes found; has the export changed?")

    # Fill and stroke are separate subpaths, so each box appears twice.
    print(f"{len(found)} panel subpaths ({len(found) // 2} boxes)")
    for start, end, box in reversed(found):
        data = data[:start] + reposition(data[start:end], args.top, args.bottom) + data[end:]
        moved = "" if (box[1], box[3]) == (args.top, args.bottom) else "  <- moved"
        print(f"  x {box[0]:8.2f}..{box[2]:8.2f}   y {box[1]:6.2f}..{box[3]:6.2f}"
              f"  ->  {args.top:.2f}..{args.bottom:.2f}{moved}")

    pdf.pages[0].Contents = pdf.make_stream(data.encode("latin-1"))
    pdf.save(args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    sys.exit(main())
