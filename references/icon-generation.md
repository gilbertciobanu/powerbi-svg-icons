# Icon Generation Workflow

Read `icon-specs.md` before generating. For a typical icon you only need sections 1–5 and section 9 (complex shapes). Skip sections 6–8 unless you need a naming reminder or template — those rules are already in SKILL.md.

---

## Dual-Variant Shortcut

When the user asks for both Regular and Filled in the same request, use this systematic transform — no need to reason through it each time:

1. **Design the Regular variant first.** All geometry decisions happen here.
2. **Derive the Filled from Regular:**
   - SVG wrapper: change `fill='none'` → `fill='#1C3879'`
   - Outer shape path: remove `fill='none'`, keep `stroke='#1C3879' stroke-width='5'` (required for visual footprint parity — do **not** add this stroke to inner marks)
   - Inner marks (exclamation bar, arrow, dot, line, etc.): change `stroke='#1C3879'` → `stroke='#FFFFFF'`, `fill='#1C3879'` → `fill='#FFFFFF'`, and `fill='none'` → `fill='#FFFFFF'` (elements that were open/stroked-only in Regular become solid white shapes in Filled). Only the outer shape path and the SVG wrapper carry `#1C3879`; every inner element is white.
3. Save both files before showing the user — one `computer://` link per variant.

---

## Generation Process

### 1. Clarify the concept
Before drawing anything, make sure you understand:
- What does this icon represent? (function, concept, data category)
- Is there an obvious real-world metaphor (funnel = filter, gear = settings, etc.)?
- Should it be **Regular** (outline/stroke style, default/idle state) or **Filled** (solid style, active/selected state)?

If the user hasn't specified, default to Regular and ask only if genuinely ambiguous. The variant is part of the filename — don't omit it.

### 2. Plan the geometry
Think in terms of the 96×96 grid before writing any path data:
- What is the primary shape? (circle, rectangle, polygon, combination)
- Where is the visual center of mass? It should sit near (48, 48)
- Does it need a secondary element (small badge, arrow, dot)?
- Is it symmetric? Prefer symmetry — it reads better at small sizes
- If it is a standard polygon, check the Shape Typology table in `icon-specs.md` section 9 for the default orientation and circumradius (R = 40 for most polygons)

Avoid complexity: if a concept needs more than 3–4 distinct shapes, simplify.
Fluent 2 icons are deliberately minimal — negative space is part of the design.

### 3. Write the SVG
Follow the template from `icon-specs.md` section 8. The constraints in SKILL.md Critical Rules are the canonical reference — single quotes, `#1C3879`, `width='100%' height='100%'`, stroke on filled paths. Fill in the `Prompt` header field with the user's request verbatim, and fill in the `Summary` field starting with `[Workflow A]` followed by a one-line record of the key decisions made: geometry method, corner rounding approach, any notable trade-offs. See `icon-specs.md` section 8 for the full list of what to include. Key geometry reminders:
- Snap coordinates to 2px increments (equivalent to 0.5px in the legacy 24×24 grid)
- `rx='12'` or higher on any rectangle (or use a C bezier path — see section 9)
- Stroke width `5` for structural lines, `4` for decorative
- All polygons → use `<path>` with **C cubic bezier** corners, not `<polygon>` and not Q beziers. Use the construction formula and reference paths in `icon-specs.md` section 9. Triangles are equilateral by default (unless the user specifies otherwise).
- **Q beziers are only valid for organic shapes** — shapes whose outline is defined by smooth curves rather than a fixed set of straight edges meeting at discrete vertices. In practice: bookmark ribbon, speech bubble, cloud, leaf, heart, wave. If a shape has a countable number of straight sides (triangle, pentagon, badge, shield, arrow, chevron), it is a polygon and must use C beziers. When in doubt, treat it as a polygon.

Before saving, do a quick spot-check for the two most common slip-ups: any double-quoted attribute, and any `currentColor` or `#000000`. Fix silently if found.

### 4. Save and show
- Before saving, apply the standard file-exists check defined in `icon-specs.md` section 6 (File Naming).
- Save to: `icons/icon-[name]-[variant].svg` (e.g. `icons/icon-filter-regular.svg`)
- Display the complete SVG file (wrapper + shapes) in a fenced `xml` code block — never just the path elements
- Provide a direct `computer://` link to the saved `.svg` file (e.g. `computer:///…/icons/icon-filter-regular.svg`) — do not create any HTML, preview page, or wrapper file
- Briefly describe the visual concept in one sentence ("A funnel shape with a horizontal line suggesting active filtering")

### 5. Iterate
The user may ask for adjustments. Common requests:
- "Make it simpler / more complex" → reduce or add shapes
- "Feels too heavy / light" → adjust stroke width or shape sizes
- "Doesn't look like X" → revisit the metaphor, try a different geometric approach

When iterating, always apply the same file-exists check as in step 4 — even for icons just created in the same session. Once the user approves, move on — don't keep polishing unprompted.

### 6. Batch mode
If the user provides a list of icon names (e.g., "create icons for: filter, reset, export, help"),
process each one in sequence using the steps above. Complete one icon fully before starting the next,
so the user can give feedback per icon if needed.

---

## Reference Examples

*These approved icons serve as style anchors. When generating new icons, aim for visual and structural consistency with these examples.*

### Example 1 — Bookmark Regular
*Organic shape: single closed path with Q beziers only at the two top rounded corners and a sharp V-notch at the bottom. Q beziers are valid here because the bookmark is an organic shape (smooth curve, no discrete polygon vertices) — see the organic/polygon rule in section 3. Wrapper `fill='none'` for Regular.*

```xml
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='100%' height='100%' fill='none'>
  <!--
    Icon Name  : Bookmark
    Style      : Minimalist, modern, flat (Fluent 2 Regular)
    Variant    : Regular
    Created    : 2026-02-27 10:00:00
    Summary    : [Workflow A] Organic shape; single closed path with Q-bezier top corners and sharp V-notch
  -->
  <path fill='none' stroke='#1C3879' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'
    d='M 30,12 L 66,12 Q 72,12 72,18 L 72,84 L 48,66 L 24,84 L 24,18 Q 24,12 30,12 Z'/>
</svg>
```

---

### Example 2 — Warning Filled
*Flat-top hexagon (section 9 reference path) as outer shape. White cutout exclamation mark using `<line>` + `<circle>`. C bezier corners. Filled variant uses explicit fill + matching stroke on path for size parity with Regular. Wrapper `fill='#1C3879'` for Filled.*

```xml
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='100%' height='100%' fill='#1C3879'>
  <!--
    Icon Name  : Warning
    Style      : Minimalist, modern, flat (Fluent 2 Filled)
    Variant    : Filled
    Created    : 2026-02-27 10:01:00
    Summary    : [Workflow A] Flat-top hexagon (section 9); white exclamation mark cutout; stroke-width 5 for footprint parity
  -->
  <path fill='#1C3879' stroke='#1C3879' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'
    d='M 84,54 C 86,50 86,46 84,42 L 72,20 C 70,16 66,14 62,14 L 34,14 C 30,14 26,16 24,20 L 12,42 C 10,46 10,50 12,54 L 24,76 C 26,80 30,82 34,82 L 62,82 C 66,82 70,80 72,76 Z'/>
  <line x1='48' y1='28' x2='48' y2='54' stroke='#FFFFFF' stroke-width='5' stroke-linecap='round'/>
  <circle cx='48' cy='64' r='4' fill='#FFFFFF'/>
</svg>
```

---

### Example 3 — Triangle Regular
*Equilateral triangle, apex up, R = 40. C bezier corners (d = 8, t = 4) at all three vertices including the apex. This is the default triangle — equilateral with apex pointing up unless the user specifies otherwise. Wrapper `fill='none'` for Regular.*

```xml
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='100%' height='100%' fill='none'>
  <!--
    Icon Name  : Triangle
    Style      : Minimalist, modern, flat (Fluent 2 Regular)
    Variant    : Regular
    Created    : 2026-02-27 10:02:00
    Summary    : [Workflow A] Equilateral triangle apex up R=40; C-bezier d=8 t=4 at all 3 corners; stroke-width 5
  -->
  <path fill='none' stroke='#1C3879' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'
    d='M 44,14 C 46,12 50,12 52,14 L 78,62 C 80,64 78,68 74,68 L 22,68 C 18,68 16,64 18,62 Z'/>
</svg>
```

---

### Example 4 — Pentagon Regular
*Pointy-top pentagon, R = 40. C bezier corners (d = 8, t = 4) at all five vertices. This is the default pentagon orientation. Wrapper `fill='none'` for Regular.*

```xml
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='100%' height='100%' fill='none'>
  <!--
    Icon Name  : Pentagon
    Style      : Minimalist, modern, flat (Fluent 2 Regular)
    Variant    : Regular
    Created    : 2026-02-27 10:03:00
    Summary    : [Workflow A] Pointy-top pentagon R=40; C-bezier d=8 t=4 at all 5 corners; stroke-width 5
  -->
  <path fill='none' stroke='#1C3879' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'
    d='M 42,12 C 44,10 52,10 54,12 L 80,32 C 82,34 84,40 84,44 L 74,72 C 74,76 68,80 64,80 L 32,80 C 28,80 22,76 22,72 L 12,44 C 12,40 14,34 16,32 Z'/>
</svg>
```

---

### Example 5 — Cart Regular
*Multi-element icon: open path for handle, closed path for basket, circles for wheels. All stroke-only for Regular. Demonstrates compound icon structure with mixed element types. Wrapper `fill='none'` for Regular.*

```xml
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 96 96' width='100%' height='100%' fill='none'>
  <!--
    Icon Name  : Cart
    Style      : Minimalist, modern, flat (Fluent 2 Regular)
    Variant    : Regular
    Created    : 2026-02-27 10:01:00
    Summary    : [Workflow A] Compound icon: open handle path + closed basket path + 2 wheel circles; stroke-width 5
  -->
  <path fill='none' stroke='#1C3879' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'
    d='M 8,18 L 18,18 L 26,40'/>
  <path fill='none' stroke='#1C3879' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'
    d='M 26,40 L 82,40 L 74,68 L 32,68 Z'/>
  <circle cx='40' cy='80' r='6' fill='none' stroke='#1C3879' stroke-width='5'/>
  <circle cx='68' cy='80' r='6' fill='none' stroke='#1C3879' stroke-width='5'/>
</svg>
```
