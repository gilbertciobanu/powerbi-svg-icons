# Icon Adapt Workflow

Read `icon-specs.md` sections 1–5 before starting. The Critical Rules in SKILL.md are the canonical constraint source — this file does not repeat them.

**Only use this workflow when the source SVG has one of the supported viewBoxes below.** Any other viewBox means the coordinates are incompatible — stop, switch to Workflow A in `icon-generation.md`, and use the source SVG as a visual reference only.

| Source viewBox | Scale factor | Integer? | Notes |
|---|---|---|---|
| `0 0 96 96` | ×1 (none) | ✓ | Paths reused as-is |
| `0 0 48 48` | ×2 | ✓ | Fluent 2 "48" size |
| `0 0 32 32` | ×3 | ✓ | Fluent 2 "32" size |
| `0 0 24 24` | ×4 | ✓ | Fluent 2 "24" size |
| `0 0 16 16` | ×6 | ✓ | Fluent 2 "16" size |
| `0 0 20 20` | ×4.8 | ✗ | Fluent 2 "20" size — produces decimals; snap all coordinates to nearest 2px increment after scaling |
| `0 0 28 28` | ×3.4286 | ✗ | Fluent 2 "28" size — produces decimals; snap all coordinates to nearest 2px increment after scaling |

Use this workflow when the user provides an existing SVG (e.g. downloaded from the Fluent 2 library or sourced externally) to recolor and integrate into the Power BI icon set. Do not generate new geometry — preserve the source paths exactly.

### Using ic_fluent_* files from the icons folder

Files named `ic_fluent_*` in the `icons/` folder are Fluent 2 source icons and are safe to use as adapt sources. They follow standard Fluent 2 viewBox conventions (most commonly `0 0 20 20`, `0 0 24 24`, or `0 0 48 48`) and use C cubic bezier corners throughout.

**Compound-path Regular icons:** Fluent 2 Regular icons often encode both the outer shape and the inner cutout (stroke area) as a single compound `d=` path using two sub-paths separated by `M`. The second sub-path traces the inner boundary in the opposite winding direction, creating an outline effect via `fill-rule='evenodd'`. This means a "Regular" Fluent icon is actually a filled shape with a hole — no `stroke` attribute. When adapting:
- If you want to preserve the compound-path technique: keep the `d=` intact, recolor to `fill='#1C3879'`, and add `fill-rule='evenodd'` if not already present.
- If you prefer our stroke-based approach (simpler, easier to iterate): use the outer boundary path from the corresponding Fluent Filled icon and apply `fill='none' stroke='#1C3879' stroke-width='5'`. This is always safe and produces an equivalent visual result.

Both techniques are valid. Note the approach used in the `Summary` header field.

**Snapping limitation for compound paths:** The Fluent stroke at 48×48 is ~2.5px thick, so the inner and outer sub-path boundaries differ by only ~2.5 source units. After ×2 scaling that gap becomes ~5px — but after 2px snapping many control points collapse onto the same coordinates, breaking the inner cutout. **Conclusion: the compound-path technique only survives snapping reliably at 96×96 source size (×1, no scaling). For 48×48 and smaller sources, either use the stroke-based approach, or use Workflow D (PPTX Normalisation) which delegates geometry scaling to PowerPoint and avoids snapping entirely.**

---

## Validation

Before making any changes, check the source SVG for the following and warn the user if found:
- `<script>` tags — flag as potentially unsafe, do not proceed without user confirmation
- `href`, `src`, or `xlink:href` attributes pointing to external URLs other than `www.w3.org` — flag each one and ask the user whether to strip or abort
- `<image>` tags with external `href` — same as above
- `<use>` elements referencing external symbol libraries — these will not resolve in Power BI's sandbox; flag and suggest inlining the referenced shape

If the SVG passes validation, proceed.

---

## Adapt Process

### 1. Recolor
Replace all color values in the SVG with the standard icon color:
- All `fill` values (except `fill='none'`) → `fill='#1C3879'`
- All `stroke` values → `stroke='#1C3879'`
- White knockout elements (`fill='#FFFFFF'` or `fill='white'`) → preserve as-is
- `currentColor` → replace with `fill='#1C3879'`
- If the user specifies a different color, use that instead of `#1C3879`

Move `fill='#1C3879'` to the `<svg>` wrapper and remove redundant `fill` attributes from child elements where possible.

### 2. Clean attributes
- Convert all double-quote attributes to single quotes throughout
- Replace hardcoded `width` and `height` px values with `width='100%' height='100%'`
- Set `viewBox='0 0 96 96'` on the `<svg>` element (apply scaling first if source was not already 96×96)
- **After scaling, snap all path coordinates to the nearest 2px increment** — round every numeric value in the `d=` attribute to the nearest even integer. Non-integer scale factors (×4.8 for 20×20, ×3.4286 for 28×28) always produce decimals; integer scale factors (×2, ×3, ×4, ×6) are usually clean but snap anyway as a safeguard. Decimals (e.g. `11.7103`, `33.1932`) cause sub-pixel blur in PowerPoint and other rasterisers. Symmetry check: for centred icons, averaged left/right x-coordinates should equal 48.
- **Axis-aligned vertex check — do this before saving:** After snapping, inspect any C bezier arc that sits at the leftmost, rightmost, topmost, or bottommost point of the icon. At these vertices the outward deviation of the control points is perpendicular to the axis (e.g. purely in x for left/right vertices). In Fluent 48×48 sources this deviation is typically only ~0.5–1 source units, which becomes ~1–2px after ×2 — and collapses to 0px after 2px snapping. The symptom: the arc becomes a straight line segment, turning a hexagon into an octagon or a smooth curve into a flat edge. **If any axis-aligned C bezier has all its x (or y) coordinates identical after snapping, the arc has collapsed.** Fix by falling back to the section 9 hand-computed reference path for that shape, or rebuilding the corner arcs with d=8 t=4 using the construction formula in `icon-specs.md` section 9.
- Ensure `xmlns='http://www.w3.org/2000/svg'` is present
- Strip `<!-- comment -->` headers from the source file — they will be replaced
- Strip SVGRepo download artifacts if present: `<!DOCTYPE>` declaration, and `<g>` wrapper elements with IDs `SVGRepo_bgCarrier`, `SVGRepo_tracerCarrier`, `SVGRepo_iconCarrier` — these add dead weight to the SVG and bloat the DAX string

### 3. Add standard header
Add the standard comment header from `icon-specs.md` section 8 inside the `<svg>` element, filling in the icon name, variant, today's date, and the `Prompt` field with the user's request verbatim. Also fill in the `Summary` field starting with `[Workflow C]` followed by a one-line record of the key adapt decisions: the source viewBox and scale factor used, whether coordinate snapping was needed, and any geometry that had to be redrawn because the viewBox was incompatible. Example values: `"[Workflow C] paths reused as-is (96×96 source); recolored + stripped SVGRepo artifacts"`, `"[Workflow C] coords scaled ×2 (48×48 source), snapped to 2px; recolored"`, `"[Workflow C] coords scaled ×4 (24×24 source); converted to single-quote attrs"`, `"[Workflow C] coords scaled ×3 (32×32 source); recolored"`, `"[Workflow C] coords scaled ×6 (16×16 source), snapped to 2px; recolored"`, `"[Workflow C] coords scaled ×4.8 (20×20 source), snapped to 2px; recolored; compound-path preserved"`, `"[Workflow C] geometry redrawn (incompatible viewBox); source used as visual reference only"`.

### 4. Save and show
- Before saving, apply the standard file-exists check defined in `icon-specs.md` section 6 (File Naming).
- Save to: `icons/icon-[name]-[variant].svg`
- Display the complete adapted SVG in a fenced `xml` code block
- Show the rendered result using a `computer://` link
- Note any changes made (e.g. "replaced `currentColor` with `#1C3879`, converted to single quotes")

---

## Notes

- Preserve the source path geometry exactly — do not simplify or redraw paths
- If both Regular and Filled variants are provided, process each as a separate file
