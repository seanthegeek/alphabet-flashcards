#!/usr/bin/env python3
"""
Bulk-convert SVG flashcards to PNG with a pure-white background.

Usage examples:
  python svg_to_png_flashcards.py --src ./svgs --out ./pngs --width 1500 --height 2500
  python svg_to_png_flashcards.py --src . --out ./pngs  # uses defaults (1500x2500)

Requires:
  pip install cairosvg
"""

import argparse
import sys
from pathlib import Path

try:
    import cairosvg
except ImportError:
    print("ERROR: cairosvg not installed. Run: pip install cairosvg", file=sys.stderr)
    sys.exit(1)

def convert_svg_to_png(svg_path: Path, out_path: Path, width: int, height: int, background: str = "#FFFFFF"):
    """
    Render a single SVG to PNG at the requested pixel size with a white background.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # CairoSVG respects either width/height in px or scale factors.
    # We set both width & height to force exact 3:5 output if desired.
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(out_path),
        output_width=width,
        output_height=height,
        background_color=background,  # ensures opaque white instead of transparent
    )

def main():
    parser = argparse.ArgumentParser(description="Convert SVG flashcards to PNG in bulk.")
    parser.add_argument("--src", type=str, default=".", help="Folder containing SVG files.")
    parser.add_argument("--out", type=str, default="./png", help="Output folder for PNG files.")
    parser.add_argument("--width", type=int, default=1500, help="PNG width in pixels (default 1500).")
    parser.add_argument("--height", type=int, default=2500, help="PNG height in pixels (default 2500).")
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.svg",
        help="Glob to match SVGs (default: *.svg)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be converted without writing files."
    )
    args = parser.parse_args()

    src_dir = Path(args.src).resolve()
    out_dir = Path(args.out).resolve()

    if not src_dir.exists():
        print(f"ERROR: Source folder not found: {src_dir}", file=sys.stderr)
        sys.exit(2)

    svgs = sorted(src_dir.glob(args.pattern))
    if not svgs:
        print(f"No SVGs found in {src_dir} matching {args.pattern}")
        sys.exit(0)

    print(f"Found {len(svgs)} SVGs in {src_dir}")
    print(f"Output → {out_dir} at {args.width}×{args.height}px")

    failures = 0
    for svg in svgs:
        # Keep the exact base name, just swap extension
        png_name = svg.stem + ".png"
        out_path = out_dir / png_name

        if args.dry_run:
            print(f"[dry-run] {svg.name}  ->  {out_path.name}")
            continue

        try:
            convert_svg_to_png(svg, out_path, args.width, args.height, background="#FFFFFF")
            print(f"✔ {svg.name}  →  {out_path.name}")
        except Exception as e:
            failures += 1
            print(f"✘ FAILED: {svg.name}  ({e})", file=sys.stderr)

    if failures:
        print(f"Done with {failures} failure(s).", file=sys.stderr)
        sys.exit(3)
    else:
        print("All done.")

if __name__ == "__main__":
    main()
