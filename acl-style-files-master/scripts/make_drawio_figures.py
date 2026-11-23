#!/usr/bin/env python3
"""Emit the two hand-drawn figures as ``.drawio`` sources.

Run from the repository root::

    python3 scripts/make_drawio_figures.py
    node scripts/export_drawio_pdf.js figures/fig1a_concept.drawio \
        figures/fig1a_concept.pdf 3.446
    node scripts/export_drawio_pdf.js figures/fig2_pipeline.drawio \
        figures/fig2_pipeline.pdf 6.323

Why a generator rather than hand-authored XML: a draw.io ``fontSize`` is in
canvas pixels, and the exporter maps the whole canvas onto the width the figure
occupies on the page.  A label's printed size is therefore

    printed_pt = fontSize_px * placed_width_pt / canvas_width_px

and that factor is different for each figure.  Authoring by eye in the draw.io
UI hides it completely: the previous revision of Figure 2 looked fine on screen
and printed its body text at 4.7 pt.  Here the factor is declared once per
figure and every size is requested in points through ``Fig.px``, so a size that
would print too small is a visible number rather than a surprise in the PDF.

Glyph coverage is the other trap.  Times New Roman, Helvetica and Arial all
lack U+2295 (oplus), U+2713 (check), U+2717 (ballot X) and U+227B (succeeds),
and Helvetica also lacks U+2192 (rightwards arrow).  A browser silently
substitutes a per-glyph fallback -- on macOS that was STSongti-SC, so the old
Figure 2 shipped with a Chinese font embedded for its check marks.  Checks,
crosses and flow arrows are therefore drawn as vector primitives here, and
``assert_safe_glyphs`` fails the build if an unsupported character reaches a
label.
"""

import html
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "figures"))

# ---------------------------------------------------------------------------
# Shared design system.  Same roles and hex codes as scripts/make_figures.py so
# the drawn figures and the plotted ones read as one set.
# ---------------------------------------------------------------------------
INK = "#1A1A1A"        # primary text, flow arrows
MUTED = "#6E7681"      # secondary text, glosses
HAIR = "#C6CDD6"       # hairline rules, unemphasised strokes
STATE_FILL = "#DCE7F5"  # reached state / conditioning context
STATE_LINE = "#4A7DB5"
SAFE_FILL = "#DDEEE6"   # recovery, safe branch, selected-for-training
SAFE_LINE = "#1F6F54"
HARM_FILL = "#F8DEDB"   # harmful branch
HARM_LINE = "#C0392B"
ZONE_NEW = "#EDF3FA"    # background: our contribution
ZONE_STD = "#F4F4F6"    # background: standard machinery
WHITE = "#FFFFFF"

SANS = "Helvetica"
SERIF = "Times New Roman"

# Every glyph a label may contain beyond ASCII, checked against the coverage of
# both families above.  Extend only after verifying the font actually has it.
SAFE_NON_ASCII = set("\u2113\u2264\u2212\u00b7\u03b8\u03c0\u03b2\u2014\u2019")


class Metrics:
    """Real advance widths, so 'does this label fit' is computed not guessed.

    Estimating character widths by eye is how the first pass of this figure
    ended up with three labels overlapping their neighbours: draw.io wraps to
    the cell width, and a line that is 8% too long silently becomes two lines
    that overrun the cell height.
    """

    FACES = {
        ("Helvetica", False, False): ("/System/Library/Fonts/Helvetica.ttc", 0),
        ("Helvetica", True, False): ("/System/Library/Fonts/Helvetica.ttc", 1),
        ("Helvetica", False, True): ("/System/Library/Fonts/Helvetica.ttc", 2),
        ("Helvetica", True, True): ("/System/Library/Fonts/Helvetica.ttc", 3),
    }
    TIMES = "/System/Library/Fonts/Supplemental/Times New Roman.ttf"

    def __init__(self):
        self._cache = {}

    def _face(self, family, bold, italic):
        key = (family, bold, italic)
        if key not in self._cache:
            from fontTools.ttLib import TTCollection, TTFont

            if family == SERIF:
                font = TTFont(self.TIMES, fontNumber=0)
            else:
                path, index = self.FACES[("Helvetica", bold, italic)]
                font = TTCollection(path).fonts[index]
            upem = font["head"].unitsPerEm
            cmap = font.getBestCmap()
            hmtx = font["hmtx"]
            self._cache[key] = (cmap, hmtx, upem)
        return self._cache[key]

    def width(self, text, size_px, family=SANS, bold=False, italic=False):
        cmap, hmtx, upem = self._face(family, bold, italic)
        total = 0
        for ch in text:
            name = cmap.get(ord(ch))
            total += hmtx[name][0] if name else int(0.5 * upem)
        return total * size_px / upem


METRICS = Metrics()


def assert_safe_glyphs(text, where):
    for ch in text:
        if ord(ch) < 128 or ch in SAFE_NON_ASCII:
            continue
        name = unicodedata.name(ch, "?")
        raise SystemExit(
            f"{where}: U+{ord(ch):04X} ({name}) is not in Helvetica/Times; "
            "draw it as a primitive or pick another character"
        )


class Fig:
    """One draw.io page, with the canvas-pixel to printed-point factor bound."""

    def __init__(self, name, canvas_w, canvas_h, placed_width_in):
        self.name = name
        self.w = canvas_w
        self.h = canvas_h
        self.pt_per_px = placed_width_in * 72.0 / canvas_w
        self.cells = []
        self.problems = []
        # Rendered ink boxes, drawn shapes and connector polylines, kept so
        # that check_collisions can find labels that sit on top of each other
        # or on top of a line. Cell geometry alone does not reveal this: a
        # centred label in a wide invisible cell can collide with a neighbour
        # whose cells never overlap.
        self.inks = []
        self.shapes = []
        self.paths = []
        self.n = 0
        # Opaque backing rectangle: the exporter crops to the content bounding
        # box, so this is what fixes the canvas size and hence the scale above.
        self.rect(0, 0, canvas_w, canvas_h, fill=WHITE, stroke="none", arc=0,
                  container=True)

    # -- units --------------------------------------------------------------
    def px(self, pt):
        """Canvas pixels for a size that must print at ``pt`` points."""
        return round(pt / self.pt_per_px)

    @staticmethod
    def _runs(markup, family, bold, italic, size_px):
        """Split inline markup into runs sharing a face and a pixel size."""
        runs, stack = [], []
        state = (family, bold, italic, float(size_px))
        for token in re.split(r"(<[^>]+>)", markup):
            if not token:
                continue
            if not token.startswith("<"):
                runs.append((html.unescape(token),) + state)
                continue
            lowered = token.lower()
            if lowered.startswith("<br"):
                runs.append(("\n",) + state)
                continue
            name = re.match(r"</?\s*([a-z]+)", lowered)
            if not name:
                continue
            if lowered.startswith("</"):
                if stack:
                    state = stack.pop()
                continue
            stack.append(state)
            family, bold, italic, size = state
            tag = name.group(1)
            if tag == "b":
                bold = True
            elif tag == "i":
                italic = True
            elif tag in ("sub", "sup"):
                size *= 0.7
            elif tag == "font":
                face = re.search(r'face="([^"]+)"', token)
                if face:
                    family = face.group(1)
                px = re.search(r"font-size:\s*([\d.]+)px", token)
                if px:
                    size = float(px.group(1))
            state = (family, bold, italic, size)
        return runs

    def fit(self, markup, w, h, size_px, bold, italic, family, pad, label):
        """Wrap the way draw.io does, and record labels that will not fit."""
        avail = w - 2 * pad
        cells, tallest = [], 0.0
        for text, fam, b, it, size in self._runs(markup, family, bold, italic,
                                                 size_px):
            for ch in text:
                if ch != "\n":
                    tallest = max(tallest, size)
                cells.append(
                    (ch, 0.0 if ch == "\n" else METRICS.width(ch, size, fam,
                                                              b, it))
                )
        size_px = tallest or size_px

        lines, cur, cur_w, word, word_w = [], "", 0.0, "", 0.0

        def flush_word():
            nonlocal cur, cur_w, word, word_w
            if not word:
                return
            if cur and cur_w + word_w > avail:
                lines.append((cur.strip(), cur_w))
                cur, cur_w = "", 0.0
            cur, cur_w = cur + word, cur_w + word_w
            word, word_w = "", 0.0

        for ch, cw in cells:
            if ch == "\n":
                flush_word()
                lines.append((cur.strip(), cur_w))
                cur, cur_w = "", 0.0
            elif ch == " ":
                flush_word()
                word, word_w = " ", cw
                flush_word()
            else:
                word, word_w = word + ch, word_w + cw
        flush_word()
        lines.append((cur.strip(), cur_w))

        for text, width in lines:
            if width - avail > 1.0:
                self.problems.append(
                    f"{self.name}: {label!r} overruns its {w:.0f} px cell by "
                    f"{width - avail:.0f} px on {text!r}"
                )
        # A text cell has no fill or border, so a line box a few pixels taller
        # than the cell is invisible; only an extra *line* actually collides
        # with whatever sits below.
        capacity = max(1, int((h + size_px * 0.35) / (size_px * 1.22)))
        if len(lines) > capacity:
            self.problems.append(
                f"{self.name}: {label!r} wraps to {len(lines)} lines but its "
                f"{h:.0f} px cell holds {capacity}"
            )
        return max((width for _, width in lines), default=0.0), len(lines)

    # -- primitives ---------------------------------------------------------
    def _id(self, prefix="c"):
        self.n += 1
        return f"{prefix}{self.n}"

    def _add(self, xml):
        self.cells.append(xml)

    def rect(self, x, y, w, h, fill, stroke, arc=6, sw=1.4, dashed=False,
             extra="", container=False):
        style = (
            f"rounded={1 if arc else 0};whiteSpace=wrap;html=1;"
            f"{'arcSize=' + str(arc) + ';' if arc else ''}"
            f"fillColor={fill};strokeColor={stroke};strokeWidth={sw};"
            f"dashed={1 if dashed else 0};"
            f"{'dashPattern=8 6;' if dashed else ''}{extra}"
        )
        cid = self._id("r")
        if not container:
            self.shapes.append(((x, y, x + w, y + h), cid))
        self._add(
            f'<mxCell id="{cid}" value="" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" '
            f'as="geometry"/></mxCell>'
        )
        return cid

    def _text(self, x, y, w, h, markup, size_pt, color=INK, bold=False,
              italic=False, align="center", valign="middle", family=SANS,
              spacing=2, extra="", pad=None, reserve=0):
        if size_pt < 6.95:
            raise SystemExit(
                f"{self.name}: {size_pt} pt label would be illegible: {markup!r}"
            )
        assert_safe_glyphs(
            html.unescape(re.sub(r"<[^>]+>", "", markup)), self.name
        )
        size_px = self.px(size_pt)
        pad = spacing + 4 if pad is None else pad
        ink_w, nlines = self.fit(markup, w - reserve, h, size_px, bold, italic,
                                 family, pad, markup)
        # Where the glyphs actually land inside the (usually invisible) cell.
        # Ascender to descender is about 0.95 em in both families, so a line
        # box (1.22 em) overstates the ink and would flag normal leading
        # between a heading and its gloss as a collision.
        ink_h = (nlines - 1) * size_px * 1.22 + size_px * 0.95
        if align == "left":
            ix = x + pad
        elif align == "right":
            ix = x + w - reserve - pad - ink_w
        else:
            ix = x + (w - reserve - ink_w) / 2
        iy = y + (h - ink_h) / 2
        boxed = "fillColor=" in extra or "strokeColor=" in extra
        self.inks.append(((ix, iy, ix + ink_w, iy + ink_h), markup, boxed))
        if boxed:
            self.shapes.append(((x, y, x + w, y + h), markup))
        # ``markup`` is HTML source; draw.io reads the attribute as HTML, so it
        # has to be XML-escaped once on the way into the attribute.
        value = html.escape(markup, quote=True)
        style = (
            f"text;html=1;strokeColor=none;fillColor=none;whiteSpace=wrap;"
            f"overflow=hidden;fontFamily={family};fontSize={size_px};"
            f"fontColor={color};align={align};verticalAlign={valign};"
            f"fontStyle={(1 if bold else 0) + (2 if italic else 0)};"
            f"spacingLeft={spacing};spacingRight={spacing};{extra}"
        )
        cid = self._id("t")
        self._add(
            f'<mxCell id="{cid}" value="{value}" style="{style}" vertex="1" '
            f'parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
            f'height="{h}" as="geometry"/></mxCell>'
        )
        return cid

    def text(self, x, y, w, h, s, size_pt, **kw):
        return self._text(x, y, w, h, html.escape(s), size_pt, **kw)

    def rich(self, x, y, w, h, markup, size_pt, **kw):
        """``markup`` may contain <i>, <b>, <sub> and <font face=...>."""
        return self._text(x, y, w, h, markup, size_pt, **kw)

    def edge(self, pts, stroke=INK, sw=2.0, arrow="classic", dashed=False,
             ortho=False, start_arrow="none", arrow_size=6, opacity=100):
        style = (
            f"edgeStyle={'orthogonalEdgeStyle' if ortho else 'none'};"
            f"rounded={1 if ortho else 0};html=1;"
            f"startArrow={start_arrow};startFill={0 if start_arrow == 'none' else 1};"
            f"endArrow={arrow};endFill={0 if arrow == 'none' else 1};"
            f"endSize={arrow_size};startSize={arrow_size};"
            f"strokeColor={stroke};strokeWidth={sw};"
            f"dashed={1 if dashed else 0};"
            f"{'dashPattern=8 6;' if dashed else ''}opacity={opacity};"
        )
        (sx, sy), (tx, ty) = pts[0], pts[-1]
        way = "".join(f'<mxPoint x="{px}" y="{py}"/>' for px, py in pts[1:-1])
        cid = self._id("e")
        # A connector is not a zero-width polyline: its stroke has width and
        # its head is a filled triangle several pixels across. Modelling it as
        # a line let an arrowhead land on a label without being reported.
        heads = [a for a in (arrow, start_arrow) if a != "none"]
        self.paths.append(
            (list(pts), cid, max(sw / 2.0, arrow_size if heads else 0.0))
        )
        self._add(
            f'<mxCell id="{cid}" value="" style="{style}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{sx}" y="{sy}" as="sourcePoint"/>'
            f'<mxPoint x="{tx}" y="{ty}" as="targetPoint"/>'
            f'{f"<Array as=\'points\'>{way}</Array>" if way else ""}'
            f"</mxGeometry></mxCell>"
        )
        return cid

    def dot(self, cx, cy, d=11, color=INK):
        # A fork marker belongs on top of its edges, so it is not a collider.
        return self.rect(cx - d / 2, cy - d / 2, d, d, color, color, arc=0,
                         sw=1, extra="shape=ellipse;", container=True)

    # -- collision detection ------------------------------------------------
    @staticmethod
    def _gap(a, b):
        """Separation between two axis-aligned boxes; negative means overlap."""
        dx = max(a[0] - b[2], b[0] - a[2])
        dy = max(a[1] - b[3], b[1] - a[3])
        return max(dx, dy)

    @staticmethod
    def _hits(seg, box, pad):
        """Does a segment pass through a box grown by ``pad``? (Liang-Barsky)"""
        (x0, y0), (x1, y1) = seg
        lo, hi = box[0] - pad, box[2] + pad
        top, bot = box[1] - pad, box[3] + pad
        t0, t1 = 0.0, 1.0
        for p, q in ((-(x1 - x0), x0 - lo), (x1 - x0, hi - x0),
                     (-(y1 - y0), y0 - top), (y1 - y0, bot - y0)):
            if p == 0:
                if q < 0:
                    return False
                continue
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
        return True

    # Text on text is only a defect once the glyphs actually meet; text on a
    # drawn border already looks wrong a few pixels before it touches.
    TEXT_CLEAR = 1.0
    SHAPE_CLEAR = 4.0
    PATH_CLEAR = 5.0

    def check_collisions(self):
        """Report labels that overlap, or sit too close to, anything else.

        The per-cell fit check cannot see any of this: every cell is
        individually well formed, and the defect exists only in the relation
        between two of them. This is the class of problem that reads as
        "text boxes covering each other" in the rendered figure.
        """
        def short(text, n=32):
            plain = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
            return plain if len(plain) <= n else plain[:n - 1] + "\u2026"

        for i, (box, label, boxed) in enumerate(self.inks):
            for other, other_label, _ in self.inks[i + 1:]:
                gap = self._gap(box, other)
                if gap < self.TEXT_CLEAR:
                    self.problems.append(
                        f"{self.name}: {short(label)!r} overlaps "
                        f"{short(other_label)!r} by {-gap:.0f} px"
                    )
            for shape, owner in self.shapes:
                if owner == label:
                    continue
                # A label sitting inside a box is that box's label, not a
                # collision; only contact with the border counts.
                if (shape[0] <= box[0] + 2 and shape[1] <= box[1] + 2
                        and shape[2] >= box[2] - 2 and shape[3] >= box[3] - 2):
                    continue
                gap = self._gap(box, shape)
                if gap < self.SHAPE_CLEAR:
                    self.problems.append(
                        f"{self.name}: {short(label)!r} is {gap:.0f} px from "
                        f"the box {short(str(owner))!r}"
                    )
            # Connectors are meant to meet boxes, so a box's own label is not
            # judged against them; only free-standing text is.
            for pts, cid, half in ([] if boxed else self.paths):
                if any(self._hits(seg, box, half + self.PATH_CLEAR)
                       for seg in zip(pts, pts[1:])):
                    self.problems.append(
                        f"{self.name}: connector {cid} comes within "
                        f"{self.PATH_CLEAR:.0f} px of {short(label)!r}"
                    )

    # -- glyphs the fonts do not have --------------------------------------
    def tick(self, cx, cy, s=20, color=SAFE_LINE, sw=3.2):
        """A check mark, drawn because no bundled font carries U+2713."""
        self.edge(
            [(cx - 0.46 * s, cy + 0.02 * s),
             (cx - 0.12 * s, cy + 0.34 * s),
             (cx + 0.48 * s, cy - 0.36 * s)],
            stroke=color, sw=sw, arrow="none",
        )

    def cross(self, cx, cy, s=17, color=HARM_LINE, sw=3.2):
        """A ballot X, drawn because no bundled font carries U+2717."""
        h = s / 2
        self.edge([(cx - h, cy - h), (cx + h, cy + h)], stroke=color, sw=sw,
                  arrow="none")
        self.edge([(cx + h, cy - h), (cx - h, cy + h)], stroke=color, sw=sw,
                  arrow="none")

    # -- output -------------------------------------------------------------
    def xml(self):
        body = "\n        ".join(self.cells)
        page_id = re.sub(r"[^A-Za-z0-9]", "", self.name)
        return (
            '<mxfile host="app.diagrams.net">\n'
            f'  <diagram name="{html.escape(self.name)}" id="{page_id}">\n'
            f'    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" '
            f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" '
            f'pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" '
            f'math="0" shadow="0">\n'
            "      <root>\n"
            '        <mxCell id="0"/>\n'
            '        <mxCell id="1" parent="0"/>\n'
            f"        {body}\n"
            "      </root>\n"
            "    </mxGraphModel>\n"
            "  </diagram>\n"
            "</mxfile>\n"
        )

    def write(self, filename):
        path = os.path.join(OUT, filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.xml())
        return path


# Math set in the body serif, matching the paper's equations.
def m(s):
    return f'<font face="{SERIF}"><i>{s}</i></font>'


def msub(base, sub):
    return (
        f'<font face="{SERIF}"><i>{base}</i><sub>{sub}</sub></font>'
    )


# ===========================================================================
# Figure 1(a) -- root refusal versus reached-state recovery
# ===========================================================================
# Placed inside a 0.545\textwidth minipage: 0.545 * 455.24 pt = 248.1 pt.
# The aspect ratio matches fig1b_reversal.pdf (3.446 in x 2.378 in) so the two
# panels of the figure* have the same height.
def build_fig1a():
    f = Fig("Figure 1a", 864, 574, 248.11 / 72.0)

    STATE_X, STATE_W = 14, 336     # the conditioning-context boxes
    FORK_X = 362
    BR_X, BR_W = 388, 232          # the two alternative futures
    MAR_X, MAR_W = 632, 220        # margin annotations
    MID = MAR_X + MAR_W / 2

    def fork(cy, state_box, safe_box, harm_box, safe_heavy):
        """One state, two futures leaving a single anchor point.

        ``safe_heavy`` thickens whichever branch the model prefers, so the
        reversal between the two bands is legible from stroke weight alone,
        without reading either margin expression.
        """
        f.edge([(STATE_X + STATE_W, cy), (FORK_X - 5, cy)], arrow="none",
               sw=2.0)
        f.dot(FORK_X, cy)
        f.edge([(FORK_X + 6, cy - 3), (BR_X - 4, safe_box)], stroke=SAFE_LINE,
               sw=4.6 if safe_heavy else 1.6)
        f.edge([(FORK_X + 6, cy + 3), (BR_X - 4, harm_box)], stroke=HARM_LINE,
               sw=1.6 if safe_heavy else 4.6)

    def branch(y, word, sym, sub, safe):
        f.rich(BR_X, y, BR_W, 60, f"<b>{word}</b> {msub(sym, sub)}", 8.0,
               reserve=30,
               extra=f"rounded=1;arcSize=14;"
                     f"fillColor={SAFE_FILL if safe else HARM_FILL};"
                     f"strokeColor={SAFE_LINE if safe else HARM_LINE};"
                     f"strokeWidth=1.6;spacingRight=34;")
        (f.tick if safe else f.cross)(BR_X + BR_W - 28, y + 30)

    # -- band (a): the root decision ---------------------------------------
    f.rect(0, 8, 864, 204, WHITE, HAIR, arc=5, sw=1.4, container=True)
    f.text(14, 14, 300, 30, "ROOT LEVEL", 8.6, bold=True, align="left")
    f.text(14, 44, 380, 26, "what refusal benchmarks score", 7.1, italic=True,
           align="left", color=MUTED, pad=0)

    f.rich(STATE_X, 99, STATE_W, 60, f'<b>harmful request</b> {m("x")}', 8.0,
           extra=f"rounded=1;arcSize=14;fillColor={STATE_FILL};"
                 f"strokeColor={STATE_LINE};strokeWidth=1.6;")
    fork(129, None, 88, 170, safe_heavy=True)
    branch(58, "refuse", "r", "0", safe=True)
    branch(140, "comply", "u", "0", safe=False)

    f.rich(MAR_X, 99, MAR_W, 32,
           f'<b>{m("m")}<sub>root</sub>({m("x")}) &gt; 0</b>', 8.2,
           color=SAFE_LINE)
    f.text(MAR_X, 133, MAR_W, 26, "refuses", 7.1, italic=True, color=MUTED)

    # Right of the descending arrow and left of the reversal callout.
    f.text(340, 244, 282, 28, "prefill, jailbreak, or drift", 7.6,
           align="left", pad=0)

    # -- band (b): the reached-state decision -------------------------------
    f.rect(0, 300, 864, 266, ZONE_NEW, STATE_LINE, arc=5, sw=1.8,
           container=True)
    f.text(14, 304, 300, 30, "REACHED STATE", 8.6, bold=True, align="left")
    f.text(14, 337, 340, 24, "what CURE-DPO scores", 7.1, italic=True,
           align="left", color=MUTED)

    # One line, in the form of Eq. (1), and the same height as the root box so
    # the two bands stay comparable. Naming x again is what ties this state to
    # the request above it. "byte-for-byte fixed" is dropped: the brace below,
    # the shared fork anchor and the caption each already say it.
    f.rich(STATE_X, 390, STATE_W, 60,
           f'{m("x")} <b>+ unsafe prefix</b> = {msub("s", "t")}', 8.0,
           extra=f"rounded=1;arcSize=12;fillColor={STATE_FILL};"
                 f"strokeColor={STATE_LINE};strokeWidth=2.4;")

    # The trajectory that produces the reached state. It leaves the *thin*
    # comply edge on purpose: the branch the model disprefers at the root is
    # the one an attack takes, so a correct root ordering does not prevent the
    # state below from being reached. Drawn after the band and the state box so
    # the arrowhead is not painted over by them.
    # It drops right of the box centre so that it clears both heading lines on
    # the way down.
    f.edge([(BR_X + 50, 200), (BR_X + 50, 228), (316, 228), (316, 386)],
           stroke=INK, sw=2.0, ortho=True)

    fork(420, None, 374, 466, safe_heavy=False)
    branch(344, "recovery", "r", "t", safe=True)
    branch(436, "harmful", "u", "t", safe=False)

    f.rich(MAR_X, 404, MAR_W, 32,
           f'<b>{m("m")}<sub>&#952;</sub>({msub("s", "t")}) &lt; 0</b>', 8.2,
           color=HARM_LINE)
    f.text(MAR_X, 438, MAR_W, 26, "continues", 7.1, italic=True, color=MUTED)

    f.edge([(BR_X + 6, 508), (BR_X + 6, 522), (BR_X + BR_W - 6, 522),
            (BR_X + BR_W - 6, 508)], stroke=MUTED, sw=1.2, arrow="none")
    f.text(284, 528, 440, 26, "same state, only the future differs", 7.1,
           italic=True, color=MUTED)

    # The callout bridges the two margin expressions, so the flip is stated
    # once in words rather than left for the reader to infer from two signs.
    f.edge([(MID, 166), (MID, 224)], stroke=HARM_LINE, sw=1.8, arrow="none",
           dashed=True)
    f.text(MAR_X, 226, MAR_W, 68, "preference reversal", 8.2, bold=True,
           color=HARM_LINE,
           extra=f"rounded=1;arcSize=16;fillColor={WHITE};"
                 f"strokeColor={HARM_LINE};strokeWidth=2.4;")
    f.edge([(MID, 296), (MID, 388)], stroke=HARM_LINE, sw=1.8, dashed=True,
           arrow_size=7)

    return f


# ===========================================================================
# Figure 2 -- what CURE-DPO changes, and what it leaves alone
# ===========================================================================
# Full \textwidth.  Two background zones carry the contribution boundary that
# Section 4.2 states in prose: stages 1-2 are new, stages 3-4 are not.
def build_fig2():
    # Panel height is set by the tallest panel's content plus one padding step.
    # The figure competes with the main text for an eight-page budget, so dead
    # space at the panel bottoms is space taken from Section 6 for nothing.
    f = Fig("Figure 2", 1600, 420, 6.323)

    PANEL_TOP, PANEL_BOT = 56, 366
    # The tags straddle the panel's top border, so they need a row of their
    # own below the zone captions or the two collide across the whole width.
    TAG_Y, TAG_H = 44, 38
    FLOW_Y = 220  # one baseline for the three arrows between panels

    def zone(x, w, fill, label):
        f.rect(x, 6, w, 372, fill, "none", arc=8, container=True)
        f.text(x + 16, 10, w - 32, 28, label, 7.8, bold=True, align="left",
               color=MUTED)

    def panel(x, w, tag, sw=1.5, stroke=INK):
        f.rect(x, PANEL_TOP, w, PANEL_BOT - PANEL_TOP, WHITE, stroke, arc=6,
               sw=sw, container=True)
        size = 8.2
        tw = METRICS.width(tag, f.px(size), SANS, True, False) + 28
        if tw > w - 8:
            f.problems.append(
                f"{f.name}: tag {tag!r} needs {tw:.0f} px on a {w} px panel"
            )
        tx = x + (w - tw) / 2
        f.rect(tx, TAG_Y, tw, TAG_H, WHITE, stroke, arc=30, sw=sw)
        f.text(tx, TAG_Y, tw, TAG_H, tag, size, bold=True)

    zone(8, 836, ZONE_NEW, "NEW: WHICH STATES, AND WHAT IS COMPARED")
    zone(856, 736, ZONE_STD, "STANDARD: HOW THE PAIRS ARE OPTIMIZED")

    # -- 1. which reached states -------------------------------------------
    P1X, P1W = 22, 330
    panel(P1X, P1W, "1  Reached states", stroke=STATE_LINE)
    f.text(P1X, 100, P1W, 26, "candidate depths (tokens)", 7.2, italic=True,
           color=MUTED)
    # The axis stops just past the mined tick; running it to the panel edge
    # would imply the sequence continues past `hard`.
    f.edge([(P1X + 14, 176), (P1X + 292, 176)], stroke=INK, sw=1.6,
           arrow="none")
    # The mined state sits at the end of the same axis, so it reads as the
    # sixth member of the candidate set rather than as a side note. Its wider
    # gap and red tick say it is not on the fixed grid.
    for dx, lab in [(24, "5"), (70, "10"), (116, "20"), (162, "40"),
                    (208, "80"), (276, "hard")]:
        cx, last = P1X + dx, dx == 276
        col = HARM_LINE if last else INK
        f.edge([(cx, 166), (cx, 186)], stroke=col, sw=2.6 if last else 1.6,
               arrow="none")
        f.text(cx - 39, 192, 78, 28, lab, 7.8, bold=last, color=col)
    f.rich(P1X + 12, 248, P1W - 24, 56,
           "mined per prompt:<br>lowest base margin", 7.4, color=HARM_LINE)

    f.edge([(P1X + P1W + 4, FLOW_Y), (P1X + P1W + 24, FLOW_Y)], sw=2.4,
           arrow_size=7)

    # -- 2. the comparison unit --------------------------------------------
    # Widest panel, heaviest border: this is the contribution.
    P2X, P2W = 380, 452
    panel(P2X, P2W, "2  Same-state pair", sw=2.4, stroke=STATE_LINE)
    f.rich(P2X + 14, 132, 180, 76,
           f'<b>{msub("s", "t")}</b><br>'
           f'<font color="{MUTED}" style="font-size:{f.px(7.2)}px">'
           f"identical state</font>", 8.6,
           extra=f"rounded=1;arcSize=12;fillColor={STATE_FILL};"
                 f"strokeColor={STATE_LINE};strokeWidth=1.6;")
    fork_x = P2X + 220
    f.edge([(P2X + 194, 170), (fork_x - 5, 170)], arrow="none", sw=1.8)
    f.dot(fork_x, 170, d=11)
    # Both branches leave one anchor point: that is the whole claim.
    f.edge([(fork_x + 6, 167), (P2X + 246, 138)], stroke=SAFE_LINE, sw=2.2)
    f.edge([(fork_x + 6, 173), (P2X + 246, 202)], stroke=HARM_LINE, sw=2.2)
    for y, word, sym, safe in [(112, "recovery", "r", True),
                               (176, "harmful", "u", False)]:
        f.rich(P2X + 246, y, 192, 52, f'<b>{word}</b> {msub(sym, "t")}', 7.8,
               reserve=26,
               extra=f"rounded=1;arcSize=14;"
                     f"fillColor={SAFE_FILL if safe else HARM_FILL};"
                     f"strokeColor={SAFE_LINE if safe else HARM_LINE};"
                     f"strokeWidth=1.6;spacingRight=30;")
        (f.tick if safe else f.cross)(P2X + 246 + 192 - 24, y + 26, s=17)

    f.rich(P2X + 14, 246, P2W - 28, 56,
           "matched on intent, safety, length,<br>and non-degeneracy", 7.2,
           italic=True, color=MUTED)
    bar_x, bar_w, split = P2X + 14, P2W - 28, 0.677
    f.rect(bar_x, 310, bar_w * split, 40, WHITE, INK, arc=0, sw=2.0)
    f.rect(bar_x + bar_w * split, 310, bar_w * (1 - split), 40, WHITE, HAIR,
           arc=0, sw=1.0)
    f.text(bar_x, 310, bar_w * split, 40, "67.7% kept", 7.4, bold=True)
    f.text(bar_x + bar_w * split, 310, bar_w * (1 - split), 40, "32.3% cut",
           7.2, color=MUTED)

    f.edge([(P2X + P2W + 4, FLOW_Y), (864, FLOW_Y)], sw=2.4, arrow_size=7)

    # -- 3. the objective, deliberately the quietest panel ------------------
    P3X, P3W = 866, 284
    panel(P3X, P3W, "3  Canonical DPO", sw=1.2, stroke=MUTED)
    cell, ncell, prefix_n = 22, 10, 6
    cx0 = P3X + (P3W - ncell * cell) / 2
    for row, (fill, line) in enumerate([(SAFE_FILL, SAFE_LINE),
                                        (HARM_FILL, HARM_LINE)]):
        y = 110 + row * 30
        for i in range(ncell):
            shared = i < prefix_n
            # Hairline shared cells against heavy branch cells, so which half
            # enters the loss survives a grayscale print.
            f.rect(cx0 + i * cell, y, cell - 3, 24,
                   STATE_FILL if shared else fill,
                   HAIR if shared else line, arc=3,
                   sw=0.8 if shared else 1.8)
    f.edge([(cx0, 172), (cx0 + prefix_n * cell - 3, 172)], stroke=MUTED,
           sw=1.2, arrow="none")
    f.edge([(cx0 + prefix_n * cell, 172), (cx0 + ncell * cell - 3, 172)],
           stroke=INK, sw=1.2, arrow="none")
    # Parallel labels, each naming what happens to the block above it.
    f.text(cx0, 182, prefix_n * cell, 26, "masked", 7.2, color=MUTED, pad=2)
    f.text(cx0 + prefix_n * cell, 182, (ncell - prefix_n) * cell, 26,
           "scored", 7.2, pad=2)

    f.rich(P3X + 14, 234, 86, 44, f'<b>{m("&#960;")}<sub>&#952;</sub></b>',
           8.4, extra=f"rounded=1;arcSize=16;fillColor={WHITE};"
                      f"strokeColor={INK};strokeWidth=2.0;")
    f.text(P3X + 102, 234, 30, 44, "\u2212", 8.4, pad=2)
    f.rich(P3X + 136, 234, 106, 44, f'<b>{m("&#960;")}<sub>ref</sub></b>',
           8.4, extra=f"rounded=1;arcSize=16;fillColor={WHITE};"
                      f"strokeColor={MUTED};strokeWidth=2.0;dashed=1;"
                      f"dashPattern=8 6;")
    f.text(P3X + 22, 300, P3W - 44, 42, "not a new loss", 7.4, bold=True,
           extra=f"rounded=1;arcSize=30;fillColor={WHITE};strokeColor={INK};"
                 f"strokeWidth=1.4;")

    f.edge([(P3X + P3W + 4, FLOW_Y), (P3X + P3W + 24, FLOW_Y)], sw=2.4,
           arrow_size=7)

    # -- 4. which states the update lands on --------------------------------
    P4X, P4W = 1172, 408
    panel(P4X, P4W, "4  Tail + anchors", sw=1.2, stroke=MUTED)
    f.text(P4X, 100, P4W, 26, "one loss per candidate state", 7.2,
           italic=True, color=MUTED)
    chip_w, gap, chips, selected = 60, 4, ["5", "10", "20", "40", "80",
                                           "hard"], {1, 3}
    span = len(chips) * chip_w + (len(chips) - 1) * gap
    cx0 = P4X + (P4W - span) / 2
    for i, sub in enumerate(chips):
        x, hot = cx0 + i * (chip_w + gap), i in selected
        # Selected states carry fill, a heavy border and a check: fill alone
        # would not survive a grayscale print.
        f.rich(x, 130, chip_w, 40, f'<b>{m("&#8467;")}<sub>{sub}</sub></b>',
               7.2, pad=3,
               extra=f"rounded=1;arcSize=18;"
                     f"fillColor={SAFE_FILL if hot else WHITE};"
                     f"strokeColor={SAFE_LINE if hot else HAIR};"
                     f"strokeWidth={2.6 if hot else 1.0};")
        if hot:
            f.tick(x + chip_w / 2, 184, s=15, sw=2.6)
    f.edge([(cx0, 200), (cx0, 208), (cx0 + span, 208), (cx0 + span, 200)],
           stroke=MUTED, sw=1.2, arrow="none")
    f.edge([(cx0 + span / 2, 208), (cx0 + span / 2, 226)], sw=1.8)
    f.text(P4X + 6, 242, P4W - 12, 26, "keep the top 2 by detached loss", 7.4,
           pad=2)

    anc_w = (P4W - 24 - 30) / 2
    for dx, word in [(0, "clean-safety"), (anc_w + 30, "benign")]:
        f.text(P4X + 12 + dx, 276, anc_w, 44, word, 7.4, bold=True,
               extra=f"rounded=1;arcSize=16;fillColor={WHITE};"
                     f"strokeColor={MUTED};strokeWidth=1.4;")
    # Anchors are additive siblings of the tail term, so they join with a plus
    # rather than sitting downstream of the top-k arrow.
    f.text(P4X + 12 + anc_w, 276, 30, 44, "+", 8.4, bold=True, pad=2)
    f.text(P4X + 12, 326, P4W - 24, 26, "always added, never selected", 7.2,
           italic=True, color=MUTED)

    # -- legend -------------------------------------------------------------
    f.edge([(654, 398), (708, 398)], stroke=INK, sw=2.4, arrow="none")
    f.text(716, 384, 130, 28, "optimized", 7.4, align="left")
    f.edge([(862, 398), (916, 398)], stroke=MUTED, sw=2.4, arrow="none",
           dashed=True)
    f.text(924, 384, 130, 28, "frozen", 7.4, align="left", color=MUTED)

    return f


if __name__ == "__main__":
    problems = []
    for build, filename in ((build_fig1a, "fig1a_concept.drawio"),
                            (build_fig2, "fig2_pipeline.drawio")):
        fig = build()
        fig.check_collisions()
        path = fig.write(filename)
        problems += fig.problems
        print(
            f"wrote {os.path.basename(path)}  canvas {fig.w}x{fig.h} px, "
            f"1 px = {fig.pt_per_px:.4f} pt, "
            f"{len(fig.problems)} layout problem(s)"
        )
    for line in problems:
        print("  !", line)
    if problems:
        raise SystemExit(1)
