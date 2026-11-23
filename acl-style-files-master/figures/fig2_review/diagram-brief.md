# Figure 2 revision brief

## Goal
- Produce a camera-ready ACL-style four-stage method banner.
- Preserve the existing scientific content and left-to-right semantics.
- Make stages 1–2 read as the contribution and stages 3–4 as supporting machinery.

## Sources
- Content/structure: `paper.tex` Figure 2 caption and `FIGURE_GUIDE.md`.
- Style: `FIGURE_GUIDE.md` shared palette and typography.
- Existing geometry: `fig2_pipeline.drawio`.

## Style contract
- Typeface: Times New Roman/Nimbus Roman throughout; serif italic for variables.
- Palette: text `#1A1A1A`, secondary `#6E7681`, state `#EEF2F7/#4A7DB5`,
  recovery `#E8F2EE/#1F6F54`, harmful `#FBEDEC/#C0392B`, frozen
  `#F4F4F6/#98A2B3`.
- No shadows, gradients, clip art, emoji, or decorative color.
- Thin neutral strokes, with stage 2 receiving the strongest outline.
- Dashed outlines exclusively encode frozen components.

## Connector semantics
- Stage arrows: processing flow, left to right.
- Panel 2 split: the identical reached state conditions both futures.
- Green branch: recovery future; red branch: harmful future.
- Bottom band: frozen base writes recovery branches and scores candidate states.

## Review priorities
1. Remove Comic Sans and restore paper-consistent serif typography.
2. Add restrained semantic fills to reduce the wireframe/sketch appearance.
3. Reduce excessive stroke weight while retaining stage-2 emphasis.
4. Improve grayscale legibility via fill and glyph redundancy.
5. Preserve the target 6.90 × 1.95 inch aspect ratio and vector output.
