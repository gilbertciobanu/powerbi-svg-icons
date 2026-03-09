#!/usr/bin/env python3
"""
Workflow D — Phase 2: Adapt the PowerPoint-exported SVG(s) and save to icons/.

Usage:
    # Single icon (reads from .workflow_state or CLI args):
    python3 factory/phase2_adapt.py [output.svg] [icon_name]

    # Batch mode (auto-detected from .workflow_state JSON):
    python3 factory/phase2_adapt.py [--yes]

Arguments (single mode — reads from .workflow_state if omitted):
    output.svg   Exported SVG in factory/ (default: factory/output.svg)
    icon_name    Target name, e.g. icon-map-regular (no .svg extension)

Flags:
    --yes        Auto-accept overwrites without prompting (batch or single)

What this script does:
    1. Reads the SVG(s) exported by PowerPoint
       Single: factory/output.svg
       Batch:  factory/output_1.svg, output_2.svg, ...
    2. Recolors all fills/strokes to #1C3879
    3. Adds fill-rule='evenodd' if a compound path is detected
    4. Converts attributes to single quotes (DAX compatibility)
    5. Normalises wrapper: xmlns, viewBox preserved from export (or 0 0 96 96), width/height='100%'
    6. Strips PowerPoint metadata and SVGRepo artifacts
    7. Adds standard icon header comment
    8. Saves to icons/<icon_name>.svg
    9. Strips media from factory/working.pptx (keeps PPTX shell)
   10. Cleans up factory/ temp files
"""

import sys, re, json, datetime, zipfile, shutil
from pathlib import Path
from xml.etree import ElementTree as ET

FACTORY_DIR = Path(__file__).parent
PROJECT_DIR = FACTORY_DIR.parent
ICONS_DIR   = PROJECT_DIR / "icons"
STATE_FILE  = FACTORY_DIR / ".workflow_state"

BRAND_COLOR = "#1C3879"


# ── State helpers ─────────────────────────────────────────────────────────────

def read_state() -> dict | list:
    """Read workflow state. Returns dict for single mode, or the full JSON
    object (with 'mode': 'batch') for batch mode."""
    if not STATE_FILE.exists():
        return {}
    text = STATE_FILE.read_text(encoding="utf-8").strip()
    # JSON batch state starts with '{'
    if text.startswith("{"):
        return json.loads(text)
    # Flat key=value (single-icon, backward compatible)
    state = {}
    for line in text.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            state[k.strip()] = v.strip()
    return state


# ── Detect SVG variant ────────────────────────────────────────────────────────

def detect_variant(content: str, source_hint: str = "") -> str:
    """Guess Regular vs Filled from the exported SVG content or source filename.

    source_hint: original filename (e.g. 'ic_fluent_notebook_32_regular.svg')
                 used as a strong signal when content analysis is ambiguous.
    """
    # Strong signal: source filename contains _regular or _filled
    if source_hint:
        lower = source_hint.lower()
        if "_regular" in lower:
            return "Regular"
        if "_filled" in lower:
            return "Filled"

    # Fallback: content analysis
    # If the source had stroke but no fill → Regular
    if re.search(r'stroke\s*=', content) and not re.search(r"fill='(?!none)[^']+'\s+stroke", content):
        return "Regular"
    # If it has fill-rule=evenodd or compound paths → likely Filled (compound)
    if re.search(r'fill-rule', content, re.IGNORECASE):
        return "Filled"
    # Default based on presence of stroke
    if re.search(r'\bstroke\b', content):
        return "Regular"
    return "Filled"


# ── Core adapt ────────────────────────────────────────────────────────────────

def adapt_svg(raw: str, icon_name: str, source_name: str, variant: str,
              target_size: str = "") -> str:
    """Apply all adapt transformations and return the final SVG string."""

    # 1. Strip DOCTYPE and XML declaration if present
    raw = re.sub(r'<\?xml[^?]*\?>', '', raw)
    raw = re.sub(r'<!DOCTYPE[^>]*>', '', raw)

    # 2. Strip SVGRepo artifacts
    raw = re.sub(r'<g[^>]+id=["\']SVGRepo_[^"\']*["\'][^>]*>.*?</g>', '', raw,
                 flags=re.DOTALL | re.IGNORECASE)

    # 3. Strip PowerPoint-added metadata groups and title/desc elements
    raw = re.sub(r'<title[^>]*>.*?</title>', '', raw, flags=re.DOTALL)
    raw = re.sub(r'<desc[^>]*>.*?</desc>', '', raw, flags=re.DOTALL)

    # 4. Recolor — replace all non-none fill and stroke values
    #    Order matters: do specific values first, then catch-alls
    raw = re.sub(r"fill\s*=\s*['\"](?!none|#1C3879)[^'\"]+['\"]",
                 f"fill='{BRAND_COLOR}'", raw, flags=re.IGNORECASE)
    raw = re.sub(r"stroke\s*=\s*['\"](?!none)[^'\"]+['\"]",
                 f"stroke='{BRAND_COLOR}'", raw, flags=re.IGNORECASE)
    raw = re.sub(r'(?i)fill\s*:\s*(?!none)[^;\"\'}\s]+',
                 f'fill:{BRAND_COLOR}', raw)  # inline style
    raw = re.sub(r'(?i)stroke\s*:\s*(?!none)[^;\"\'}\s]+',
                 f'stroke:{BRAND_COLOR}', raw)

    # 5. Resolve PowerPoint translate wrapper: <g transform='translate(tx ty)'>
    #    PowerPoint offsets the shape by its slide position (1"=96pt → translate(-96,-96))
    def apply_translate(content):
        m = re.search(
            r"<g[^>]+transform=['\"]translate\((-?[\d.]+)[,\s]+(-?[\d.]+)\)['\"][^>]*>(.*?)</g>",
            content, re.DOTALL
        )
        if not m:
            return content
        tx, ty = float(m.group(1)), float(m.group(2))

        def shift_path(pm):
            tag = pm.group(0)
            dm = re.search(r"d=['\"]([^'\"]*)['\"]", tag)
            if not dm:
                return tag
            tokens = re.split(r'([MmLlHhVvCcSsQqTtAaZz])', dm.group(1))
            out, cmd = [], None
            for tok in tokens:
                tok = tok.strip()
                if not tok:
                    continue
                if re.match(r'^[MmLlHhVvCcSsQqTtAaZz]$', tok):
                    cmd = tok; out.append(tok)
                else:
                    nums = re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?', tok)
                    cu = (cmd or 'M').upper()
                    shifted = []
                    for i, n in enumerate(nums):
                        v = float(n)
                        if cu == 'H':
                            shifted.append(f"{v+tx:.3f}".rstrip('0').rstrip('.'))
                        elif cu == 'V':
                            shifted.append(f"{v+ty:.3f}".rstrip('0').rstrip('.'))
                        elif cu == 'A' and i % 7 == 5:
                            shifted.append(f"{v+tx:.3f}".rstrip('0').rstrip('.'))
                        elif cu == 'A' and i % 7 == 6:
                            shifted.append(f"{v+ty:.3f}".rstrip('0').rstrip('.'))
                        elif cu == 'A':
                            shifted.append(n)
                        elif i % 2 == 0:
                            shifted.append(f"{v+tx:.3f}".rstrip('0').rstrip('.'))
                        else:
                            shifted.append(f"{v+ty:.3f}".rstrip('0').rstrip('.'))
                    out.append(' '.join(shifted))
            new_d = ''.join(out)
            return tag.replace(dm.group(0), f"d='{new_d}'")

        fixed = re.sub(r'<path[^>]*/>', shift_path, m.group(3))
        return content.replace(m.group(0), fixed)

    raw = apply_translate(raw)

    # 6. Detect compound paths and add fill-rule='evenodd' if missing
    #    Fix: use [Mm] to count moveto commands (not \bM\b which misses M followed by digit)
    def add_fill_rule(m):
        tag = m.group(0)
        dm = re.search(r"d=['\"]([^'\"]*)['\"]", tag)
        if dm and len(re.findall(r'[Mm]', dm.group(1))) >= 2 and 'fill-rule' not in tag:
            return tag.replace('<path ', "<path fill-rule='evenodd' ", 1)
        return tag
    raw = re.sub(r'<path [^/]*/>', add_fill_rule, raw)
    raw = re.sub(r'<path [^>]*>.*?</path>', add_fill_rule, raw, flags=re.DOTALL)

    # 6b. Detect viewBox from exported SVG (Shape.Export uses source coords e.g. 0 0 48 48;
    #     "Save as Picture" produces 0 0 96 96 after translate is baked in)
    _vb_m = re.search(r'viewBox=["\']([^"\']+)["\']', raw, re.IGNORECASE)
    detected_viewbox = _vb_m.group(1).strip() if _vb_m else "0 0 96 96"

    # 6c. Compute viewBox scaling if target_size is specified
    #     Shape.Export preserves the source viewBox regardless of PPTX shape size,
    #     so we rescale the viewBox to the target and wrap paths in <g transform='scale()'>.
    #     This avoids touching individual coordinates (Workflow D's purpose).
    vb_scale = None  # None = no scaling needed
    if target_size:
        vb_parts = detected_viewbox.split()
        if len(vb_parts) == 4:
            src_w, src_h = float(vb_parts[2]), float(vb_parts[3])
            if "x" in target_size:
                tgt_w, tgt_h = [int(x) for x in target_size.split("x")]
            else:
                tgt_w = tgt_h = int(target_size)
            sx = tgt_w / src_w if src_w else 1
            sy = tgt_h / src_h if src_h else 1
            if abs(sx - 1.0) > 0.001 or abs(sy - 1.0) > 0.001:
                detected_viewbox = f"0 0 {tgt_w} {tgt_h}"
                vb_scale = (sx, sy)

    # 7. Convert double-quoted attributes to single quotes
    #    Walk attr by attr so we don't break SVG path data
    def dq_to_sq(m):
        return m.group(0).replace('"', "'")
    raw = re.sub(r'\s[\w:@-]+=(?:"[^"]*")', dq_to_sq, raw)

    # 7. Normalise the <svg> wrapper
    #    Remove old width/height px values, set canonical attributes
    raw = re.sub(r"<svg([^>]*)>", _normalise_svg_tag, raw, count=1)

    # 8. Determine wrapper fill for header
    wrapper_fill = "none" if variant == "Regular" else BRAND_COLOR

    # 9. Strip existing comment headers from the source
    raw = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)

    # 10. Rebuild with standard header
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    display_name = icon_name.replace("-", " ").title()

    inner = raw
    # Extract just what's between <svg...> and </svg>
    body_match = re.search(r'<svg[^>]*>(.*)</svg>', inner, re.DOTALL)
    body = body_match.group(1).strip() if body_match else inner.strip()

    # Wrap body in <g transform='scale()'> if viewBox was rescaled
    if vb_scale:
        sx, sy = vb_scale
        if abs(sx - sy) < 0.001:
            scale_attr = f"{sx:.6g}"
        else:
            scale_attr = f"{sx:.6g},{sy:.6g}"
        body = f"<g transform='scale({scale_attr})'>\n    {body}\n  </g>"

    size_info = f" target {target_size} px;" if target_size else ""
    # Compute shape inches from target_size for display
    if target_size and "x" in target_size:
        tw, th = target_size.split("x")
        shape_desc = f"{int(tw)/72:.3f}\"×{int(th)/72:.3f}\""
    elif target_size:
        shape_desc = f"{int(target_size)/72:.3f}\"×{int(target_size)/72:.3f}\""
    else:
        shape_desc = "1.333\"×1.333\""

    result = (
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='{detected_viewbox}'"
        f" width='100%' height='100%' fill='{wrapper_fill}'>\n"
        f"  <!--\n"
        f"    Icon Name  : {display_name}\n"
        f"    Style      : Minimalist, modern, flat (Fluent 2 {variant})\n"
        f"    Variant    : {variant}\n"
        f"    Created    : {now}\n"
        f"    Prompt     : Workflow D — PPTX normalisation from {source_name}\n"
        f"    Summary    : [Workflow D] paths normalised via PowerPoint {shape_desc} export;"
        f"{size_info} recolored to {BRAND_COLOR}; no coordinate scaling applied\n"
        f"  -->\n\n"
        f"  {body}\n\n"
        f"</svg>"
    )

    return result


def _normalise_svg_tag(m: re.Match) -> str:
    """Replace the <svg ...> opening tag with our canonical version."""
    attrs = m.group(1)
    # We'll rebuild in the caller — just return a placeholder marker
    # (actual rebuild is done in the final assembly above)
    return "<svg_PLACEHOLDER>"


# ── PPTX cleanup — strip media, keep shell ────────────────────────────────────

def strip_pptx_media(pptx_path: Path):
    """Remove all media files from the PPTX ZIP, keeping the shell intact."""
    if not pptx_path.exists():
        return

    tmp = pptx_path.with_suffix(".tmp.pptx")
    with zipfile.ZipFile(str(pptx_path), "r") as zin, \
         zipfile.ZipFile(str(tmp), "w", zipfile.ZIP_DEFLATED) as zout:

        for item in zin.infolist():
            # Skip media files
            if item.filename.startswith("ppt/media/"):
                continue

            data = zin.read(item.filename)

            # Clean [Content_Types].xml — remove SVG and PNG overrides
            if item.filename == "[Content_Types].xml":
                ct = data.decode("utf-8")
                ct = re.sub(r'<Default Extension="svg"[^/]*/>', '', ct)
                ct = re.sub(r'<Override PartName="/ppt/media/[^"]*"[^/]*/>', '', ct)
                data = ct.encode("utf-8")

            # Clean slide .rels — remove image relationships
            elif item.filename.endswith(".xml.rels"):
                rels = data.decode("utf-8")
                rels = re.sub(
                    r'<Relationship[^>]+Type="[^"]*relationships/image"[^/]*/>\s*',
                    '', rels
                )
                data = rels.encode("utf-8")

            # Clean slide XML — remove pic shapes
            elif re.match(r'ppt/slides/slide\d+\.xml$', item.filename):
                xml = data.decode("utf-8")
                xml = re.sub(r'<p:pic\b.*?</p:pic>', '', xml, flags=re.DOTALL)
                data = xml.encode("utf-8")

            zout.writestr(item, data)

    pptx_path.unlink()
    tmp.rename(pptx_path)


# ── Batch processing ──────────────────────────────────────────────────────────

def run_batch(state: dict, auto_yes: bool):
    """Process all icons from a batch state JSON."""
    icons = state.get("icons", [])
    target_size = state.get("target_size", "")
    n = len(icons)

    print(f"\n{'='*60}")
    print(f"  Batch mode — Phase 2 — {n} icon(s)")
    print(f"{'='*60}\n")

    # Check which output files exist
    existing = []
    for entry in icons:
        out_svg = ICONS_DIR / f"{entry['icon_name']}.svg"
        if out_svg.exists():
            existing.append(out_svg.name)

    if existing and not auto_yes:
        print(f"  WARNING: {len(existing)} icon(s) already exist:")
        for name in existing:
            print(f"    - {name}")
        confirm = input("  Overwrite all? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            sys.exit(0)

    # Process each icon
    results = []
    errors = []
    for entry in icons:
        slide_num = entry["slide"]
        source_name = entry["source"]
        icon_name = entry["icon_name"]
        svg_in = FACTORY_DIR / f"output_{slide_num}.svg"

        print(f"\n  ── Slide {slide_num}: {icon_name} ──")

        if not svg_in.exists():
            print(f"    ✗ Missing: {svg_in.name}")
            errors.append((icon_name, "output file missing"))
            continue

        # Read and detect variant (non-interactive: auto-accept)
        raw = svg_in.read_text(encoding="utf-8", errors="replace")
        variant = detect_variant(raw, source_hint=source_name)
        print(f"    Variant detected: {variant}")

        # Adapt
        adapted = adapt_svg(raw, icon_name, source_name, variant,
                            target_size=target_size)
        out_svg = ICONS_DIR / f"{icon_name}.svg"
        out_svg.write_text(adapted, encoding="utf-8")
        print(f"    ✓ Saved: icons/{out_svg.name}")
        results.append((icon_name, variant, out_svg.name))

        # Clean up this output file
        svg_in.unlink(missing_ok=True)

    # Cleanup: strip media from working.pptx, remove state
    print(f"\n  Cleaning up factory/...")
    pptx_path = FACTORY_DIR / "working.pptx"
    if pptx_path.exists():
        strip_pptx_media(pptx_path)
        print(f"    ✓ Media stripped from working.pptx")

    STATE_FILE.unlink(missing_ok=True)

    # Summary table
    print(f"\n{'='*60}")
    print(f"  Phase 2 complete — {len(results)}/{n} icons saved")
    if errors:
        print(f"  ({len(errors)} error(s))")
    print(f"{'='*60}\n")

    print(f"  {'Icon Name':<35} {'Variant':<10} {'File'}")
    print(f"  {'─'*35} {'─'*10} {'─'*30}")
    for name, variant, fname in results:
        print(f"  {name:<35} {variant:<10} {fname}")
    if errors:
        print()
        for name, err in errors:
            print(f"  ✗ {name}: {err}")

    print(f"""
  Next steps:
    • Review the SVGs visually
    • Generate DAX files (Workflow B)
""")


# ── Single-icon processing ────────────────────────────────────────────────────

def run_single(state: dict, auto_yes: bool):
    """Process a single icon (original behavior)."""
    # Resolve arguments / state
    # Filter out --yes from argv for positional arg parsing
    args = [a for a in sys.argv[1:] if a != "--yes"]

    if len(args) >= 2:
        svg_in_arg = args[0]
        icon_name  = args[1]
    elif len(args) == 1:
        svg_in_arg = args[0]
        icon_name  = state.get("icon_name")
    else:
        svg_in_arg = "output.svg"
        icon_name  = state.get("icon_name")

    if not icon_name:
        print("ERROR: icon_name not provided and .workflow_state not found.")
        print("Usage: python3 phase2_adapt.py [output.svg] [icon_name]")
        sys.exit(1)

    svg_in = Path(svg_in_arg)
    if not svg_in.is_absolute():
        svg_in = FACTORY_DIR / svg_in_arg
    if not svg_in.exists():
        print(f"ERROR: Exported SVG not found: {svg_in}")
        print("Have you run the ExportIconAsSVG macro in PowerPoint yet?")
        sys.exit(1)

    source_name = state.get("source", svg_in.name)
    target_size = state.get("target_size", "")
    out_svg     = ICONS_DIR / f"{icon_name}.svg"

    print(f"\nExported SVG : {svg_in.name}")
    print(f"Output icon  : {out_svg.name}")

    # Check for overwrite
    if out_svg.exists() and not auto_yes:
        print(f"\nWARNING: {out_svg.name} already exists.")
        confirm = input("Overwrite? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Aborted.")
            sys.exit(0)

    # Read and adapt
    print("\n[1/4] Reading exported SVG...")
    raw = svg_in.read_text(encoding="utf-8", errors="replace")

    print("[2/4] Detecting variant...")
    variant = detect_variant(raw, source_hint=source_name)
    print(f"      Detected: {variant}")
    if not auto_yes:
        try:
            v_confirm = input(f"      Accept '{variant}'? (Enter = yes, or type Regular/Filled): ").strip()
            if v_confirm in ("Regular", "Filled"):
                variant = v_confirm
        except EOFError:
            pass  # Non-interactive, accept detected variant

    print("[3/4] Applying adapt (recolor, fill-rule, attrs, header)...")
    adapted = adapt_svg(raw, icon_name, source_name, variant,
                        target_size=target_size)

    # Save to icons/
    out_svg.write_text(adapted, encoding="utf-8")
    print(f"      ✓ Saved: icons/{out_svg.name}")

    # Cleanup
    print("[4/4] Cleaning up factory/...")
    svg_in.unlink(missing_ok=True)

    pptx_path = FACTORY_DIR / "working.pptx"
    if pptx_path.exists():
        strip_pptx_media(pptx_path)
        print(f"      ✓ Media stripped from working.pptx (shell preserved)")

    STATE_FILE.unlink(missing_ok=True)

    print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Phase 2 complete.

  Icon saved : icons/{out_svg.name}

  Next steps:
    • Review the SVG visually
    • Generate DAX file (Workflow B)
    • Run phase1 again for the next icon
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    auto_yes = "--yes" in sys.argv
    state = read_state()

    # Detect batch vs single from state format
    if isinstance(state, dict) and state.get("mode") == "batch":
        run_batch(state, auto_yes)
    else:
        run_single(state, auto_yes)


if __name__ == "__main__":
    main()
