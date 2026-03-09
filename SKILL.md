---
name: powerbi-svg-icons
description: Create, adapt, and normalise SVG icons and generate DAX image measures for Power BI. Use whenever the user mentions Power BI icons, SVG icons, Fluent icons (ic_fluent_*), recoloring or cleaning up an SVG, normalising icon geometry via PowerPoint (Workflow D), or generating DAX measure strings from SVGs. Trigger on any of these — even if the user doesn't say "skill" or "workflow" explicitly.
---

# Power BI SVG Icon Skill

This skill covers four workflows. Use the routing table below to pick the right one, then read the relevant reference file before starting work.

## Workflow Routing

| User intent | Workflow |
|---|---|
| "Create a [name] icon" / "design an icon for X" | **A — Icon Creation** |
| "Both regular and filled" | **A — Icon Creation** (dual-variant, see note in generation ref) |
| "Convert this DAX" / "turn icon into a measure" | **B — DAX Generation** |
| User provides a source SVG to recolor/clean and its `viewBox` is one of the supported sizes (`0 0 16 16`, `0 0 20 20`, `0 0 24 24`, `0 0 28 28`, `0 0 32 32`, `0 0 48 48`, `0 0 96 96`) — including any `ic_fluent_*` file in the `icons/` folder | **C — Adapt** |
| User provides a source SVG with any other `viewBox` | **A — Icon Creation** (use the source SVG as visual reference only; do not attempt to reuse its paths) |
| User wants to normalise an `ic_fluent_*` icon's geometry without coordinate scaling (avoids snap artifacts) | **D — PPTX Normalisation** |

**Key distinction for source SVGs:** Adapting (C) is valid for the seven supported viewBox sizes listed above. Scale factors for each are in `references/icon-adapt.md`. The ×4.8 (20×20) and ×3.4286 (28×28) scales produce non-integer coordinates — mandatory coordinate snapping applies. Any other viewBox means the geometry is incompatible — treat the source as a sketch and redraw in Workflow A.

**When to prefer D over C:** Fluent source SVGs contain decimal coordinates (e.g. `23.9999`, `27.75`). After integer scaling these remain clean, but Workflow C's mandatory 2px snap can collapse inner cutout boundaries in compound-path Regular icons. Workflow D delegates geometry normalisation to PowerPoint (1"×1" resize → SVG export), which avoids all snapping. Use D when the source is `ic_fluent_*` at any standard size and the icon has compound paths (Regular icons with inner cutouts).

---

## Critical Rules — Apply to Every SVG Generated

These are the canonical constraints. Reference files point back here rather than repeating them — if you notice a conflict, this section wins.

These override Claude's SVG defaults. Violations break Power BI rendering.

- **NEVER double quotes** — all attributes use single quotes: `fill='#1C3879'`, not `fill="#1C3879"`
- **NEVER `currentColor` or black** — color must always be hardcoded to `#1C3879`. Regular icons use `fill='none'` + `stroke='#1C3879'`; Filled icons use `fill='#1C3879'`. Neither `currentColor` nor `black` nor `#000000` is ever valid.
- **NEVER hardcoded px dimensions** — always `width='100%' height='100%'`, never `width='24'`
- **NEVER omit the `icon-` prefix** — filename is `icon-[name]-[variant].svg`, saved to `icons/`
- **NEVER save outside `icons/`** — the only valid save paths are `icons/icon-[name]-[variant].svg` and `icons/icon-[name]-[variant]_dax.txt`; never the root folder or any other location
- **NEVER create HTML files, preview pages, or any extra files** — outputs are `.svg` and `_dax.txt` only; do not create wrappers, viewers, or artifacts of any kind
- **ALWAYS show the complete SVG** — after saving, display the full `<svg>...</svg>` file in a fenced `xml` code block; never summarize or show only path elements
- **NEVER silently overwrite an existing SVG file** — ALWAYS stop and ask the user first ("Overwrite / Keep both / Cancel"), regardless of how the request is phrased, including "recreate", "redo", "update", or "replace"

## Completion Message

After finishing any workflow (or batch), the agent must end with a short summary listing every icon produced. Use a table for batch results, a single line for one icon.

**Single icon:**
> Saved `icon-briefcase-regular.svg` (Regular, 96×96 px)

**Batch / multi-icon:**

| Icon | Variant | Size | File |
|---|---|---|---|
| briefcase | Regular | 96×96 | `icon-briefcase-regular.svg` |
| calendar | Filled | 48×48 | `icon-calendar-filled.svg` |

For Workflow B (DAX), list the `.txt` files instead. For Workflow D, include the Phase (1 or 2) context so the user knows what step comes next:
> **Phase 1 done** — created `factory/working.pptx` with 3 slides. Open `macro-seed.pptm` and run **ExportBatchSVGs**, then say "done".

---

## Workflow A — Icon Creation

Use when the user wants to design or iterate on one or more SVG icons.

1. Read `references/icon-generation.md` before generating anything
2. Confirm the icon concept(s) with the user — name, purpose, any visual hint
3. Generate the SVG following the spec; save each file to the `icons/` subfolder
4. Show the SVG in a fenced `xml` code block and as a rendered preview via `computer://` link
5. Iterate based on feedback until the user approves the icon
6. If the user provides a list of icon names, process each one in sequence using the same steps

**Output:** `icons/icon-[name]-[variant].svg`

---

## Workflow B — DAX Measure Generation

Use when the user wants to turn approved icons into Power BI DAX measures.

1. Read `references/icon-dax.md` before generating anything
2. Identify which icons to process — single file or a batch from the `icons/` folder
3. For each icon, produce the DAX measure string and save it as a `.txt` file
4. Name each `.txt` file using the same base name as the SVG with a `_dax` suffix

**Output:** `icons/icon-[name]_dax.txt`

---

## Workflow C — Adapting Existing Icons

Use when the user provides an existing SVG (e.g. from the Fluent 2 library) to recolor and integrate into the icon set.

1. Read `references/icon-adapt.md` before doing anything
2. Validate, recolor, and clean the source SVG following the adapt workflow
3. Save the result to the `icons/` subfolder with the standard naming convention
4. Show the adapted SVG as a fenced `xml` code block and a rendered `computer://` preview

**Output:** `icons/icon-[name]-[variant].svg`

---

## Workflow D — PPTX Normalisation

Use when an `ic_fluent_*` icon needs geometry normalisation without coordinate scaling or snapping — typically for compound-path Regular icons where Workflow C's 2px snap would collapse the inner cutout.

This workflow supports **single-icon** and **batch** modes. Phase 1 and 2 are run by the agent; between them the user runs a VBA macro in PowerPoint.

### Shape Size (`--size`)

The `--size` flag controls the PPTX shape dimensions (default: **96** px = 96/72 = 1.333").

- `--size 96` → square 96×96 px → 1.333"×1.333" shape
- `--size 48` → square 48×48 px → 0.667"×0.667" shape
- `--size 96x64` → explicit W×H → 1.333"×0.889" shape

**Proportionality check:** If the target aspect ratio doesn't match the source SVG's viewBox (e.g., source is 48×48 but target is 96×64), Phase 1 exits with an error. The agent should then ask the user to choose a proportional size or confirm the non-proportional size explicitly (using `WxH` format).

In batch mode, a single `--size` applies to all icons. If the user doesn't mention groups with different resolutions, assume the entire batch shares the same target.

### Single-Icon Mode

**Phase 1 (agent runs):**
```
python3 factory/phase1_create_pptx.py [--size 96] <source_svg> <output_icon_name>
```
- Validates the source SVG (security check: scripts, external URLs)
- Embeds SVG natively at target size (default 96 px = 1.333") in `factory/working.pptx` (1 slide)
- Saves `factory/.workflow_state` with icon name, source, and target_size for Phase 2

**Windows step (user runs — in PowerPoint):**
Open `factory/macro-seed.pptm` → Alt+F8 → run `ExportIconAsSVG`

**Phase 2 (agent runs):**
```
python3 factory/phase2_adapt.py
```

### Batch Mode

The user describes which icons to normalize conversationally (e.g. "normalize briefcase, building, and calendar"). The agent resolves source filenames and output names, then runs:

**Phase 1 (agent runs):**
```
python3 factory/phase1_create_pptx.py --size 96 --batch \
  ic_fluent_briefcase_48_regular.svg:icon-briefcase-regular \
  ic_fluent_building_48_regular.svg:icon-building-regular \
  ic_fluent_calendar_48_regular.svg:icon-calendar-regular
```
- Validates all SVGs upfront (fail-fast) + proportionality check per icon
- Creates one slide per icon in `factory/working.pptx` (slide 1 = icon 1, etc.)
- Saves batch state as JSON in `factory/.workflow_state` (includes `target_size`)
- Prints a summary table: slide → source → target name

**Windows step (user runs — in PowerPoint):**
Open `factory/macro-seed.pptm` → Alt+F8 → run `ExportBatchSVGs`
- Exports `output_1.svg`, `output_2.svg`, ... `output_N.svg` to `factory/`

**Phase 2 (agent runs):**
```
python3 factory/phase2_adapt.py --yes
```
- Auto-detects batch mode from JSON state
- Loops through all entries: reads `output_{i}.svg`, detects variant, adapts, saves to `icons/`
- Non-interactive: auto-accepts detected variant, `--yes` skips overwrite prompts
- Cleans up all `output_*.svg` files, strips media from working.pptx, deletes state
- Prints summary table: icon name → variant → saved file

**Output:** `icons/icon-[name]-[variant].svg` (one per icon)

### Common Details

**Phase 2 adapt steps** (same for single and batch):
- Resolves PowerPoint's `translate(-96 -96)` offset if present (bakes into path coordinates)
- Preserves the viewBox from the export (Shape.Export keeps source coords, e.g. `0 0 48 48`)
- Applies full adapt: recolor to `#1C3879`, `fill-rule='evenodd'` for compound paths, single quotes, `width='100%' height='100%'`, strips metadata
- Adds standard header comment with `[Workflow D]` tag in Summary
- Strips media from `factory/working.pptx` shell (preserves file for OneDrive stability)

### VBA Macros

Both macros live in `factory/macro-seed.pptm`. Full source: `references/workflow-d-macros.md`

- **`ExportIconAsSVG`** — single-icon: exports slide 1 shape → `factory/output.svg`
- **`ExportBatchSVGs`** — batch: exports each slide → `factory/output_1.svg`, `output_2.svg`, ... `output_N.svg`

### Notes

- `factory/macro-seed.pptm` must exist — created once manually by the user; contains both macros in a standard Module; `factory/` must be a trusted location in PowerPoint Trust Center
- OneDrive for Business returns SharePoint cloud URLs from `Presentation.Path`, so the macros use a folder picker instead; files from OneDrive folders open in Protected View (Shapes.Count = 0), so the macros copy to `%TEMP%` before opening
- `Shape.Export ppShapeFormatSVG` only works on native SVG shapes — that is why Phase 1 embeds SVG natively via ZIP/XML manipulation rather than inserting as a picture
- Phase 2 preserves the viewBox from the export (typically `0 0 48 48` for 48px Fluent sources)
- `factory/` is the temporary workspace — files there are in-flight, not final
- The `ic_fluent_*` source remains in `icons/` unchanged; Workflow D produces a new file alongside it
- After Phase 2, run Workflow B to generate DAX measures

---

## Notes

- Always work within the `icons/` subfolder for all output files
- Icon creation and DAX generation are intentionally separate steps — don't combine them unless the user explicitly asks
- Batch DAX processing is designed to run after the user has approved the final icon versions
- `factory/` is for in-flight work only — never reference factory files as final deliverables
