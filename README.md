# powerbi-svg-icons

> **Audience: end users.** This file is human-facing — it is not read by Claude and contains no skill instructions. For the agent entry point, see `SKILL.md`.

A Claude skill for designing, adapting, and converting SVG icons into Power BI DAX measures. Follows the [Fluent 2 Design System](https://fluent2.microsoft.design) — minimalist, flat, consistent.

## Four workflows

| Workflow | When to use |
|---|---|
| **A — Create** | Design a new icon from a concept description |
| **B — Convert** | Turn an approved SVG into a ready-to-paste DAX measure |
| **C — Adapt** | Recolor and clean an existing SVG (e.g. from the Fluent 2 library) |
| **D — Normalise** | Normalise Fluent 2 icons with complex geometry via PowerPoint (preserves compound paths without coordinate snapping) |

## Documentation

Full guide, prompt examples, design specifications, and tips:
→ [`docs/powerbi-svg-icons-skill-guide.md`](docs/powerbi-svg-icons-skill-guide.md)

## Quick start

Point Claude Desktop / Cowork to your local folder directly — no installation needed.

To install the skill on Claude.ai, go to **Customize** → **Skills** → **"+"** → **Upload a skill** — upload a ZIP of this repository.

> **Note:** Workflows A, B, and C work in any Claude setup. Workflow D (Normalise via PowerPoint) requires a local setup — the Python scripts and `factory/` workspace need to run on your machine.

Try these prompts:

```
Create a "filter" icon, both Regular and Filled variants.
```

```
Normalise ic_fluent_notebook_32_regular, ic_fluent_calendar_48_regular — batch.
```

```
Convert icon-filter-regular and icon-filter-filled to DAX measures.
```