# Icon Specifications
Power BI Button Icons — Consistent Design System
Last updated: 2026-03-04

## Quick-Read Guide

You don't need to read this whole file for every task. Use this table:

| Task | Sections to read |
|---|---|
| Creating or adapting any icon | 1, 2, 3, 4, 5 |
| Drawing a polygon with 5+ vertices (hexagon, pentagon, star…) | + section 9 |
| Naming a file or checking if it exists before saving | + section 6 |
| Building the SVG wrapper from scratch | + section 8 |
| DAX string formatting | See `icon-dax.md` |

---

Design reference: Fluent 2 Design System (Microsoft)
Icons follow Fluent 2 conventions: rounded geometry, flat fills, optical sizing at
16/20/24/28/32px. See: https://fluent2.microsoft.design

**Note on Fluent 2 source icons:** The GitHub repository (github.com/microsoft/fluentui-system-icons)
has had inconsistent public access — some folders may be restricted. If you need reference geometry
for a specific icon, search for the icon name on the Fluent 2 design site above, or use the Figma
community file as a fallback. Do not block icon generation waiting for source access — use the
spec below and your best geometric judgment.

---

## 1. Color

| Property          | Value                                                    |
|-------------------|----------------------------------------------------------|
| Fill color        | `#1C3879` (dark navy — highest contrast on light backgrounds) |
| Accent / highlight| `#FFFFFF` (white cutout or inner ring)                   |
| Opacity variants  | 100% primary shapes, 35% decorative/secondary elements   |
| Color mode        | Single flat fill — no gradients, no shadows              |
| Override support  | Color is **hardcoded** — `currentColor` does NOT work for measure-based SVGs in Power BI. SVGs are sandboxed as images with no CSS context to inherit from. |

Theme palette (data colors — avoid for icons, reserve for data series):
`#4C49ED` `#0EA5E9` `#1C3879` `#607D8B` `#BFCAD0` `#4FD18B` `#AFAEFE` `#D14F4F`

---

## 2. Size & ViewBox

| Property        | Value                                                      |
|-----------------|------------------------------------------------------------|
| ViewBox         | `0 0 96 96` (96×96 coordinate grid)                       |
| Width / Height  | `100%` — never hardcoded px, lets Power BI scale freely   |
| Optical padding | ~8px inset from viewBox edge on all sides (shapes within ~8–88 range) |
| Aspect ratio    | Always 1:1 (square)                                        |

The 96×96 grid gives comfortable coordinate space for complex paths and bezier curves. Since Power BI scales via `width='100%' height='100%'`, the viewBox size has no effect on rendered size. Existing icons in the set using `0 0 24 24` remain valid and render identically — no need to redraw them.

---

## 3. Style

- **Style family:** Minimalist, modern, flat (Fluent 2 "Regular" weight variant)
- **Fills:** Solid shapes only — no gradients, no drop shadows, no glows
- **Strokes:** Used sparingly; `stroke-width` 4–5 in the 96×96 grid, `stroke-linecap='round'`
- **Corner style:** `C` cubic bezier arcs at every corner — see Shape Typology in section 9 for per-shape defaults. Rectangles may use `<rect rx>` as a shorthand.
- **Shape language:** Geometric, circular nodes preferred; avoid overly complex paths
- **State variants:** Regular (idle) / Filled (active or selected) — match Fluent 2 convention
- **Filled variant stroke:** Filled icons must include `stroke='#1C3879' stroke-width='5'` in addition to the fill. The stroke extends outward from the path edge, matching the visual footprint of the Regular variant. Without it, the Filled icon appears smaller than its Regular counterpart at the same coordinates.
- **Center circle:** Solid fill (no inner ring cutout) — inner rings lose definition below ~32px and make the icon look fragmented. Solid center is preferred for small UI sizes.

---

## 4. Stroke & Weight

| Property       | Value                                             |
|----------------|---------------------------------------------------|
| Stroke width   | `5` for structural lines; `4` for secondary/decorative lines |
| Minimum element| No shape or stroke thinner than `4` (breaks at small sizes) |
| Line cap       | `round`                                           |
| Line join      | `round`                                           |

---

## 5. Pixel Grid

- Anchor points: snap to 2px increments minimum (e.g. `cx='14'`, not `cx='13.3'`) — equivalent to 0.5px in the legacy 24×24 grid
- Shapes centered on the 96×96 grid; primary focus point at (48, 48)
- Prefer horizontally or vertically symmetric compositions

---

## 6. File Naming

Convention: `icon-[name]-[variant].svg` (lowercase, hyphen-separated)
Variant values: `regular` (outline/stroke, default/idle state) or `filled` (solid, active/selected state)
Examples: `icon-settings-regular.svg`, `icon-filter-regular.svg`, `icon-filter-filled.svg`
No spaces in filenames.

### File-Exists Check (canonical — referenced by all workflows)

For each file about to be saved, check whether `icons/icon-[name]-[variant].svg` already exists. When saving multiple files in one request (e.g. both Regular and Filled), check each one independently — a clear path for one does not imply a clear path for the other.

If the file exists, resolve its timestamp using this priority order — the timestamp must always be a date so the archived filename carries chronological meaning:
1. `Created` field from the SVG comment header
2. File's last-modified time from the filesystem (`mtime`) — always available in practice
3. Current datetime as a last resort — at minimum establishes an upper bound (the old file predates this moment)

Note to the user which source was used.

Prompt the user:</p>

> *"icon-[name]-[variant].svg already exists (Created: [timestamp]). Overwrite, keep both, or cancel?"*

- **Overwrite** — replace the existing file
- **Keep both** — rename the existing file by appending its timestamp in `YYYY-MM-DD-HHMMSS` format (e.g. `icon-filter-regular_2026-02-27-143022.svg`), then save the new file under the original name. After saving, tell the user the old version was archived as `icon-[name]-[variant]_[timestamp].svg`.
- **Cancel** — abort, do not save

---

## 7. SVG File Structure

- Single `<svg>` element, no nested `<svg>`
- Descriptive `<!-- comment -->` header inside each file (name, style, date)
- No embedded fonts, no external references
- No JavaScript
- Compatible with: Power BI, browsers, Figma, Illustrator

---

## 8. Template Header

The wrapper `fill` differs by variant — use the correct template for each.

**Regular** — wrapper `fill='none'` (no child element needs inherited fill):

```xml
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='100%' height='100%' fill='none'>
  <!--
    Icon Name  : [name]
    Style      : Minimalist, modern, flat (Fluent 2 Regular)
    Variant    : Regular
    Created    : [YYYY-MM-DD HH:MM:SS]
    Prompt     : [user's request, verbatim]
    Summary    : [Workflow X] [key design decisions — e.g. "5-pt star: trig coords R=36/r=14, Q-bezier tips (section 9), stroke-width 5"]
  -->

  <!-- shapes go here -->

</svg>
```

**Filled** — wrapper `fill='#1C3879'` (child paths inherit fill; white cutouts use explicit `fill='#FFFFFF'`):

```xml
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='100%' height='100%' fill='#1C3879'>
  <!--
    Icon Name  : [name]
    Style      : Minimalist, modern, flat (Fluent 2 Filled)
    Variant    : Filled
    Created    : [YYYY-MM-DD HH:MM:SS]
    Prompt     : [user's request, verbatim]
    Summary    : [Workflow X] [key design decisions — e.g. "derived from Regular; filled solid + stroke-width 5 for footprint parity"]
  -->

  <!-- shapes go here -->

</svg>
```

**What to write in `Summary`:** One line starting with the workflow tag (`[Workflow A]`, `[Workflow B]`, `[Workflow C]`, or `[Workflow D]`), followed by the decisions that explain *why* this SVG looks the way it does. Include any of the following that apply:
- **Workflow tag** (required, always first): `[Workflow A]` for icon creation, `[Workflow C]` for adapting existing icons, `[Workflow D]` for PPTX normalisation. Workflow B (DAX generation) does not produce SVG files, so it does not appear here.
- Geometry method: `trig coords R=40/r=16`, `rect + circle compound`, `single closed path`, `adapted from source`
- Corner rounding: `C-bezier d=8 t=4 (section 9)`, `C-bezier d=6 t=3 tight`, `rx=12 rectangle`, `Q-bezier organic corners` (Q is valid for non-polygon organic shapes only)
- Source handling (Adapt workflow): `paths reused as-is (96×96 source)`, `coords scaled ×4 (24×24 source)`, `geometry redrawn (incompatible viewBox)`
- Variant derivation: `derived from Regular`, `shared path — fill/stroke only`
- Any notable trade-off: `inner radius increased for legibility`, `simplified to 2 shapes for small-size clarity`

**Important:** All SVG attributes use **single quotes** (not double quotes) — this is required
for safe embedding in DAX measure strings, which are wrapped in double-quoted DAX strings.
If working with an externally sourced SVG (e.g. downloaded or created by another author),
replace all double-quote attributes with single quotes before embedding in DAX.

---

## 9. Polygon Corners — Shape Typology and C Bezier Construction

### Why C beziers, not Q beziers or `stroke-linejoin`

Fluent 2 uses **cubic `C` bezier arcs** at every polygon corner. They produce a true circular-arc quality that `Q` beziers (parabolic, asymmetric) cannot match, and they are reliable on Filled variants where `stroke-linejoin='round'` only rounds stroke joins, not the filled shape itself.

---

### Shape Typology

Use this table as the default for every polygon icon. Override only when the user specifies otherwise.

| Shape | Default orientation | Corner method | Circumradius / size |
|---|---|---|---|
| Circle / Ellipse | — | `<circle>` or `<ellipse>` element | fit to context |
| Rectangle / Square | — | `<rect rx='12'>` or C bezier path | fit to context |
| Triangle (equilateral) | Apex up | C bezier at all 3 corners | R = 40 |
| Pentagon | Pointy-top (apex up) | C bezier at all 5 corners | R = 40 |
| Hexagon | Flat-top (horizontal top/bottom edges) | C bezier at all 6 corners | R = 40 |
| Star (5-point) | Point up | C bezier at 5 outer tips only; `L` through inner concave points (keep sharp) | outer R = 40, inner r ≈ 24 (r/R ≈ 0.61 — Fluent proportion; do not use r = 16, arms become too thin at small sizes) |
| Other regular polygon | Single point/flat edge up as visually natural | C bezier at all corners | R = 40 |

**Circumradius R = 40** (center 48,48) gives paths that extend to roughly x/y 8–88, matching the Fluent 2 footprint. Do not use R = 36 for new icons.

---

### C Bezier Corner Construction

For each corner vertex **V**, with **û_in** = unit vector of the incoming edge and **û_out** = unit vector of the outgoing edge:

```
S   = V − d × û_in      ← start of corner arc (d units before vertex, on incoming edge)
CP1 = V − t × û_in      ← first control point (pulls toward vertex from incoming side)
CP2 = V + t × û_out     ← second control point (pulls toward vertex from outgoing side)
E   = V + d × û_out     ← end of corner arc (d units after vertex, on outgoing edge)
```

**Magic constant:** `t = d × 0.5523`   where `0.5523 = (4/3)(√2 − 1)`. This is the standard factor for approximating a circular arc with a cubic bezier. For practical values snap t to the nearest integer:

| Corner tightness | d | t (= d × 0.5523, rounded) | Visual corner radius |
|---|---|---|---|
| Tight (Fluent-like) | 4 | 2 | ≈ 4 px |
| Moderate | 6 | 3 | ≈ 6 px |
| Generous | 8 | 4 | ≈ 8 px |

**Path structure:**
```
M [S at first corner]
C [CP1] [CP2] [E]    ← corner arc
L [S at next corner] ← straight edge
C [CP1] [CP2] [E]    ← next corner arc
... Z
```

Z closes the final straight edge back to M (the first S point).

---

### Reference Paths (R = 40, center 48,48, d = 8, t = 4)

For each path below, Regular variant uses `fill='none' stroke='#1C3879' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'`; Filled variant uses `fill='#1C3879' stroke='#1C3879' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'` (stroke required for size parity — see section 3).

**Equilateral Triangle — apex up**
Vertices: top (48,8), lower-right (82,68), lower-left (14,68)
```xml
<path d='M 44,14 C 46,12 50,12 52,14 L 78,62 C 80,64 78,68 74,68 L 22,68 C 18,68 16,64 18,62 Z'/>
```

**Hexagon — flat-top** *(horizontal top and bottom edges)*
Vertices: right (88,48), upper-right (68,14), upper-left (28,14), left (8,48), lower-left (28,82), lower-right (68,82)
```xml
<path d='M 84,54 C 86,50 86,46 84,42 L 72,20 C 70,16 66,14 62,14 L 34,14 C 30,14 26,16 24,20 L 12,42 C 10,46 10,50 12,54 L 24,76 C 26,80 30,82 34,82 L 62,82 C 66,82 70,80 72,76 Z'/>
```

**Pentagon — pointy-top** *(single apex at top)*
Vertices: top (48,8), upper-right (86,36), lower-right (72,80), lower-left (24,80), upper-left (10,36)
```xml
<path d='M 42,12 C 44,10 52,10 54,12 L 80,32 C 82,34 84,40 84,44 L 74,72 C 74,76 68,80 64,80 L 32,80 C 28,80 22,76 22,72 L 12,44 C 12,40 14,34 16,32 Z'/>
```

---

### Stars

Stars use C beziers **only at the 5 outer tips**. Inner concave points use straight `L` lines — sharp concave angles are what make a star recognisable as a star. Outer tips R = 40, inner points r ≈ 24.

**Why r ≈ 24 and not the "classic" r ≈ 15?** The mathematically pure 5-pointed star uses r/R ≈ 0.382 (≈ 15 at R = 40), but at 16–24px render sizes the arms become hairline-thin and the icon loses legibility. Fluent 2 uses r/R ≈ 0.61 (r ≈ 24), producing wider arms that read clearly at all sizes. Use this proportion by default.

**Adapting from ic_fluent_star_48_*:** The compound-path Regular technique does not survive ×2 snapping — the notch gap between inner and outer sub-paths collapses to 0px after coordinate snapping. Always use the stroke-based approach: take the outer boundary path from `ic_fluent_star_48_filled.svg`, scale ×2, snap, and apply `fill='none' stroke='#1C3879' stroke-width='5'`.
