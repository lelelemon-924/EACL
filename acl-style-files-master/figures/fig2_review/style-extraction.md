# Reference style extraction

## Reference 1 — three-paradigm overview

### Palette
- Background: `#FFFFFF`.
- Cream process/input fill: `#FEF2CA`.
- Peach output fill: `#FFE5CA`.
- Blue method/intermediate fill: `#D9E8FD`.
- Primary stroke, arrows, and text: near-black `#111111`.
- Accent cyan used by graph/robot artwork: approximately `#59BED3`.
- Total working colors: six.

### Typography
- Heading and body labels: rounded handwritten/Comic Sans family.
- Stage labels: bold, approximately 20–24 px in the source raster.
- Small explanatory lines: approximately 17–20 px.
- Math is absent; our figure will retain serif italic for math to protect symbol
  legibility.

### Shape and arrow language
- Rounded rectangles with 10–15 px radius.
- Thick black box strokes, approximately 4 px.
- Thick solid black arrows with large triangular heads.
- No shadow or gradient.
- Dashed black horizontal rules separate major paradigms.

### Layout rhythm
- Repeated left-to-right pipeline rows.
- Main objects share one visual baseline.
- Labels are centered inside boxes rather than floating around them.
- Moderate whitespace; cards are compact around their content.
- A single icon or visual object is the focal point of each step.

## Reference 2 — detailed method architecture

### Palette
- Background and panel backgrounds: white / very light gray.
- Main method fill: pale blue.
- Stage-label fill: pale cream.
- Entity fill: pale green.
- Unknown fill: pale blue.
- Incomplete/contrast accent: dark red.
- Primary stroke/text: near-black.

### Typography
- Rounded handwritten font for panel titles and explanatory labels.
- Strong hierarchy: numbered stage tags > module titles > annotations.
- Dense paragraphs are contained in bordered cards.

### Shape and arrow language
- Large light-gray rounded panel groups.
- Numbered cream title tags overlap or sit on panel boundaries.
- Thick dark borders on primary modules; thin gray borders on secondary content.
- Straight or orthogonal black arrows; no decorative colored connectors.

### Layout rhythm
- Dense but grid-aligned.
- Text and graph visuals occupy separate, bounded regions.
- Major modules are large and readable; annotations attach to edges or sit in
  dedicated footer tags.

## Synthesized style contract for Figure 2

- Use Comic Sans MS for titles, labels, and short explanatory text.
- Keep formula variables and the DPO equation in Times New Roman italic.
- Use rounded, pale cards with thick dark outlines and cream numbered title tags.
- Use one shared content baseline and one shared annotation/footer baseline.
- Use thick black pipeline arrows with large heads.
- Keep the manuscript's existing semantic green/red/blue colors inside modules,
  but use the references' cream/blue card backgrounds to organize composition.
- Remove floating legend prose; express frozen status as compact dashed tags.
- Do not import robot or graph clip art: those images encode agents/KGs in the
  references but have no direct semantic role in CURE-DPO.

## Semantic justification

- Depth ticks represent the five fixed token depths and one mined state.
- The branch split represents two futures decoded from one identical state.
- The equation card represents the canonical same-state DPO objective.
- Six loss chips represent the six actual candidate-state losses.
- Dashed frozen tags represent the frozen base/reference policy.
- No decorative token bars, robots, databases, or graph icons are introduced.
