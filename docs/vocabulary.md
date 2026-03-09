# Power BI SVG Icon Skill — Vocabulary & Prompting Guide

> **Who this is for:** end users who want to prompt the skill more precisely and get consistent results on the first attempt. Knowing the right word often saves a full back-and-forth iteration.

---

## Contents

1. [Workflow Trigger Words](#workflow-trigger-words)
2. [Variants — Regular and Filled](#variants--regular-and-filled)
3. [Shape & Geometry](#shape--geometry)
4. [Rendering & Coordinates](#rendering--coordinates)
5. [Text in Icons](#text-in-icons)
6. [Color & Fill](#color--fill)
7. [Power BI & DAX](#power-bi--dax)
8. [Prompt Overrides (Style Adjustments)](#prompt-overrides-style-adjustments)

---

## Workflow Trigger Words

These words tell the skill **which workflow to run**. Using them explicitly avoids the skill having to guess.

| Word or phrase | Effect |
|---|---|
| **create**, design, generate, draw | Workflow A — design a new icon from scratch |
| **adapt**, recolor, convert from Fluent, integrate | Workflow C — take an existing SVG file and recolor/clean it |
| **normalise**, normalize, PPTX normalisation, compound path | Workflow D — normalise Fluent 2 icon geometry via PowerPoint (avoids snapping artifacts) |
| **convert to DAX**, export to DAX, generate measure, to DAX | Workflow B — produce a Power BI DAX measure from an approved SVG |
| **both variants** | Generate Regular _and_ Filled in the same request |
| **then convert to DAX** | Chain Workflows A/C and B in a single session — design first, then export |
| **batch**, list of icon names | Process multiple icons in a single request (Workflows A, C, or D) |
| **at Npx**, `--size N`, resolution | Set the target pixel size for Workflow D (default 96 px); e.g. "at 72px" or "at 24px" |
| **done** | Handoff signal — tell Claude the VBA macro step is finished and Phase 2 can run |

> **Tip:** Workflows are intentionally separate. If you don't say "then convert to DAX", the skill stops after saving the SVG and waits for your approval before proceeding.

[↑ Back to contents](#contents)

---

## Variants — Regular and Filled

Every icon exists in two visual states. The variant is part of the filename and must always be specified.

| Term | Meaning | Synonyms / aliases |
|---|---|---|
| **Regular** | Outline style — a stroked contour with a transparent interior; represents the default or idle state | outline, hollow, stroke-style, contour |
| **Filled** | Solid style — the entire shape is filled; represents the active or selected state | solid, bold, active, opaque |

> Both variants occupy the same visual footprint (same outer boundary). The Filled variant adds a matching stroke to its path so it appears the same size as the Regular.

[↑ Back to contents](#contents)

---

## Shape & Geometry

### Core concepts

| Term | Definition |
|---|---|
| **Path** | The primary SVG drawing element (`<path>`). Draws arbitrary curves and straight lines using the `d=` attribute. Most icons are one or two paths. |
| **Stroke** | A line drawn along both sides of a path centerline. `stroke-width='5'` means 2.5 px extending on each side of the path edge. Controls the visible thickness of Regular icons. |
| **Fill** | The color applied to the interior of a closed shape. Filled icons use `fill='#1C3879'`; Regular icons use `fill='none'`. |
| **Silhouette** | The solid outer boundary of an icon shape — what you see when you squint at it. For compound-path icons (e.g. adapted Fluent 2 Regular icons), the silhouette is the outer closed path. |
| **Compound path** | Two closed paths combined into one element using a fill rule. The outer path defines the silhouette; the inner path punches a hole through it. Fluent 2 Regular icons use this approach instead of stroke. Generated icons use stroke instead — same visual result, simpler geometry. |
| **Wall thickness** | The visible border width of an icon — how thick the outline looks. For stroke icons: equals `stroke-width` (5 px). For compound-path icons: the gap between the outer and inner contours (~5 px in Fluent 2). Both approaches produce the same 5 px visual weight. |
| **Footprint** | The total visual area an icon occupies. Regular and Filled variants are designed to match footprint — they should appear the same size when displayed side by side. |
| **Visual weight** | How heavy or light the icon looks at small sizes. Heavier = thicker strokes, bolder shapes. The skill targets Fluent 2's weight (5 px wall). |

### Corners and curves

| Term | Definition |
|---|---|
| **rx** | The corner radius attribute on a `<rect>` element. `rx='8'` produces a moderately rounded rectangle. Higher value = more rounded. The skill uses a three-tier system: `rx='12'` (simple bold shapes), `rx='8'` (complex icons), `rx='4'` (secondary elements). |
| **Q bezier / quadratic bezier** | A smooth curve defined by one control point. Used at polygon vertices (hexagons, stars, pentagons) for subtle rounding. Simpler than a cubic bezier. |
| **C bezier / cubic bezier** | A smooth curve defined by two control points. More precise than Q; used in Fluent 2 source icons for corner rounding. |
| **Vertex** | A corner point of a polygon. The skill rounds only sharp or acute vertices (< 90°) and keeps obtuse ones as straight lines — preserving the shape's geometric identity. |
| **Straight edge** | An `L` command in a path — a straight line between two anchor points. Preferred over curved edges for polygon sides. |

### Icon structure terms

| Term | Synonyms | Definition |
|---|---|---|
| **Cutout** | knockout, punch-through, hole | A shape that appears transparent because it is rendered as a white element (`fill='#FFFFFF'`) over a colored background. Used inside Filled icons to create internal details (exclamation mark, window, slot). |
| **White cutout** | white knockout | Same as cutout — white fill used to create the illusion of a hole. Not actual transparency (SVG transparency would make it invisible in DAX). |
| **Inner ring** | hollow center | A ring or donut shape with a circular hole in the center. Avoided in this skill — the hole loses definition below ~32 px. Solid center discs are preferred. |
| **Optical padding** | inset, breathing room | The empty space between the icon shape and the viewBox edge. The skill targets ~8 px on each side, keeping shapes within the 8–88 range of the 96×96 grid. |

[↑ Back to contents](#contents)

---

## Rendering & Coordinates

| Term | Definition |
|---|---|
| **ViewBox** | The coordinate space of an SVG. This skill uses `0 0 96 96` — a 96×96 grid. The rendered pixel size is controlled by Power BI, not by the viewBox. |
| **Coordinate snapping** | Rounding all path coordinates to whole numbers. Required after scaling a 48×48 source icon ×2, because odd source coordinates produce decimals that cause sub-pixel blur in PowerPoint. |
| **Sub-pixel** | A coordinate that falls between whole pixels (e.g. `11.7`, `33.19`). Causes anti-aliasing blur in PowerPoint's SVG renderer. Always snap to integers after scaling. |
| **Anchor point** | A point on a path — defined by an x,y coordinate pair. The skill snaps anchor points to 2 px increments. |
| **Scale factor** | The multiplier applied to path coordinates when adapting a smaller source icon to 96×96. Fluent 2 48×48 source → ×2. Fluent 2 24×24 source → ×4. |
| **Symmetry check** | After scaling and snapping, verify that left/right x-coordinates average to 48 (the horizontal center). Ensures the icon is still optically centered. |
| **SVGRepo artifacts** | Invisible wrapper elements (`SVGRepo_bgCarrier`, `SVGRepo_tracerCarrier`, `SVGRepo_iconCarrier`) that SVGRepo adds to downloaded SVGs. They bloat the DAX string without contributing anything visual. The skill strips them automatically during Workflow C. |

[↑ Back to contents](#contents)

---

## Text in Icons

Relevant for pill icons, KPI badges, and any icon where a label appears inside the shape.

| Term | Definition |
|---|---|
| **Glyph-to-path** | Converting font characters to SVG `<path>` data using the fontTools library. The resulting icon renders identically on every machine regardless of installed fonts. Use for fixed labels (unit names, column headers). Also called: path conversion, font-to-path, outline text. |
| **SVG `<text>` element** | Native SVG text node. The viewer's system supplies the font at render time. Smaller and simpler than glyph-to-path, but font-dependent. Use when the text value will change via DAX. |
| **Dynamic text** | Text whose value changes per row or per measure (e.g. a KPI value). Must use the SVG `<text>` element — glyph-to-path is fixed at design time and cannot be swapped via DAX. |
| **fontTools** | The Python library the skill uses for glyph-to-path conversion. It reads `.ttf` files from the `fonts/` folder and generates path data for each character. |
| **Pill icon** | An icon with a wide rectangular shape and fully rounded ends (rx = half the height), used as a label or badge container. Requires a non-square viewBox (e.g. 348×96). |

[↑ Back to contents](#contents)

---

## Color & Fill

| Term | Definition |
|---|---|
| **Navy / `#1C3879`** | The primary icon color. All shapes default to this unless you specify a different color. |
| **White cutout / `#FFFFFF`** | White fill used inside Filled icons to create internal details that appear transparent. Actual SVG transparency (`opacity`, `fill='none'`) is also valid but `#FFFFFF` is the safe default for Power BI. |
| **`currentColor`** | A CSS keyword that inherits color from the parent element. **Does not work in Power BI** — SVGs embedded as data URIs are sandboxed as images with no CSS context. The skill always replaces `currentColor` with `#1C3879` during Workflow C. |
| **Flat color** | A single solid fill with no gradients, shadows, or transparency effects. Required — Power BI's SVG sandbox does not render gradients reliably. |
| **Opacity** | A value between 0 and 1 controlling element transparency. The skill uses 35% opacity for decorative or secondary elements where applicable. |

[↑ Back to contents](#contents)

---

## Power BI & DAX

| Term | Definition |
|---|---|
| **Data URI** | The format used to embed SVGs directly in a DAX string: `"data:image/svg+xml;utf8," & "<svg ...>"`. No external file reference — the entire icon lives inside the measure. |
| **DAX measure** | A Power BI formula that returns a value. Icon measures return a data URI string. Must have **Data Category = Image URL** set in the Modeling tab for the image to render. |
| **Image URL (Data Category)** | The Power BI setting that tells the visual engine to treat a measure's string value as an image source rather than plain text. Required for every icon measure. |
| **Single quotes (SVG attributes)** | All SVG attributes in this skill use single quotes (`stroke='#1C3879'`), not double quotes. The entire SVG sits inside a double-quoted DAX string — using single quotes inside it avoids the need for escape characters on every attribute, keeping the measure readable and safe to paste. |

[↑ Back to contents](#contents)

---

## Prompt Overrides (Style Adjustments)

Say these phrases in your prompt to override the skill's defaults.

| Say this | Effect |
|---|---|
| **"both variants"** | Generate Regular and Filled in the same request |
| **"then convert to DAX"** | Also run Workflow B after creating or adapting the icon |
| **"softer corners"** or **"more rounded"** | Apply larger curves at polygon vertices (hexagons, triangles, stars) |
| **"sharp corners"** | Skip vertex rounding on polygons — keep all angles as points |
| **`rx='12'`** (or any value) | Override the default corner radius on a rectangle |
| **"simpler"** | Reduce to fewer shapes; drop secondary details |
| **"more complex"** or **"more detailed"** | Add internal elements, labels, or additional shapes |
| **"glyph-to-path"** or **"path conversion"** | Convert text to SVG paths using a font from the `fonts/` folder |
| **"dynamic text"** or **"not path-converted"** or **"SVG text"** | Use a `<text>` element instead — text value will be replaced via DAX |
| **"in `#607D8B`"** (or any hex) | Override the default navy color with a specific hex value |
| **"Regular only"** or **"Filled only"** | Generate only one variant (default is Regular if unspecified) |
| **"adapt"** + filename | Run Workflow C on an existing SVG file |
| **"normalise"** + filename(s) | Run Workflow D on one or more Fluent 2 icons via PowerPoint |
| **"at Npx"** | Set the target resolution for Workflow D (e.g. "normalise map at 72px") |
| **"batch"** or provide a list | Process multiple icons in a single request (Workflows A, C, or D) |
| **"done"** | Tell Claude the VBA macro step is finished — triggers Phase 2 |

### File conflict responses

When a file already exists, the skill asks what to do. Reply with one of these:

| Reply | Effect |
|---|---|
| **overwrite** | Replace the existing file |
| **keep both** | Archive the old file with its timestamp appended to the name, then save the new file under the original name |
| **cancel** | Abort — do not save anything |

[↑ Back to contents](#contents)

---

> **Quick summary of the most impactful words:**
> `Regular`, `Filled`, `both variants`, `adapt`, `normalise`, `convert to DAX`, `batch`, `at Npx`, `done`, `glyph-to-path`, `dynamic text`, `softer corners`, `sharp corners`
