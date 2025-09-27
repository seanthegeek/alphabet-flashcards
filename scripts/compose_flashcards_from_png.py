#!/usr/bin/env python3
"""
Compose A–Z preschool flashcards (SVG + PNG) from illustration-only images.

Key features:
- Dynamic font auto-fit for top-left letters ("A a") and bottom word.
- Glyph-top alignment for text (prevents clipping of tall glyphs like 'J').
- Illustration vertically centered between letters and word areas.
- Optional manual font-size overrides and font path.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

# ----------------------------------
# Font candidates (used if --font not provided)
# ----------------------------------

FONT_CANDIDATES = [
    "../fonts/Andika-Regular.ttf",
    "fonts/Andika-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

# ----------------------------------
# Helpers
# ----------------------------------


def load_mapping(mapping_path: Path) -> List[Tuple[str, str]]:
    """Load letter→word mapping from JSON and return as a sorted list of (letter, word)."""
    with mapping_path.open("r", encoding="utf-8") as f:
        mapping: Dict[str, str] = json.load(f)
    pairs = [(k.upper(), v) for k, v in mapping.items()]
    pairs.sort(key=lambda kv: kv[0])
    return pairs


def find_illustration(
    images_dir: Path,
    word: str,
    exts: Iterable[str] = (".png", ".jpg", ".jpeg", ".webp"),
) -> Optional[Path]:
    """Find an illustration file for the given word (case-insensitive, common extensions)."""

    def normalize(name: str) -> str:
        return "".join(ch for ch in name.lower() if ch.isalnum())

    want = normalize(word)

    for p in images_dir.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in exts:
            continue
        if normalize(p.stem) == want:
            return p
    return None


def ensure_out_dirs(out_dir: Path) -> Tuple[Path, Path]:
    """Create OUT/svgs and OUT/pngs and return their paths."""
    svg_dir = out_dir / "svgs"
    png_dir = out_dir / "pngs"
    svg_dir.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)
    return svg_dir, png_dir


def resolve_font_path(preferred: Optional[Path]) -> Optional[Path]:
    """Return a usable TrueType font path from preferred or candidates, else None."""
    if preferred is not None and preferred.exists():
        return preferred
    for candidate in FONT_CANDIDATES:
        resolved = Path(candidate).expanduser()
        if resolved.exists():
            return resolved
    return None


def load_font_exact(font_path: Optional[Path], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a TrueType font at an exact size; fall back to PIL default if unavailable."""
    if font_path is not None and font_path.exists():
        try:
            return ImageFont.truetype(str(font_path), size=size)
        except OSError:
            return ImageFont.load_default()
    return ImageFont.load_default()


def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> Tuple[int, int]:
    """Return (width, height) of rendered text with the given font."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])


def autofit_font(
    text: str,
    max_w: int,
    max_h: int,
    font_path: Optional[Path],
    start_size: int = 24,
    step: int = 4,
    ceiling: int = 2048,
) -> Tuple[ImageFont.ImageFont, int]:
    """
    Find the largest TrueType font size that fits within (max_w, max_h).
    Returns (font, size). If no TTF is available, returns PIL default and a heuristic size.
    """
    dummy = Image.new("RGB", (max(1, max_w), max(1, max_h)))
    draw = ImageDraw.Draw(dummy)

    if font_path is None or not font_path.exists():
        default_font = ImageFont.load_default()
        nominal = max(24, min(max_w, max_h) // 2)
        return (default_font, nominal)

    size = max(8, start_size)
    last_good_size = size
    last_good_font: ImageFont.ImageFont = ImageFont.truetype(str(font_path), size=size)

    while size <= ceiling:
        test_font = ImageFont.truetype(str(font_path), size=size)
        w, h = measure_text(draw, text, test_font)
        if w <= max_w and h <= max_h:
            last_good_font = test_font
            last_good_size = size
            size += step
            continue
        break

    return (last_good_font, last_good_size)


def fit_image(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    """Return a resized copy of img that fits within (max_w, max_h) preserving aspect."""
    w, h = img.size
    scale = min(max_w / w, max_h / h)
    new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
    return img.resize(new_size, Image.LANCZOS)


def pil_to_base64_png(img: Image.Image) -> str:
    """Encode a PIL image to base64 PNG string."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    s = hex_str.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"Invalid hex color: {hex_str}")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return (r, g, b)

# ----------------------------------
# Layout
# ----------------------------------


class Layout:
    """Layout constants for the flashcard."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        self.margin = int(0.05 * width)

        # Top letters region (box used for auto-fit)
        self.letters_x = int(0.05 * width)
        self.letters_y = int(0.06 * height)
        self.letters_box_w = int(0.42 * width)
        self.letters_box_h = int(0.16 * height)

        # Word region near bottom
        self.word_y = int(0.80 * height)
        self.word_box_w = int(0.90 * width)
        self.word_box_h = int(0.12 * height)

# ----------------------------------
# SVG composition
# ----------------------------------


def compose_svg(
    canvas_w: int,
    canvas_h: int,
    letters_text: str,
    letters_fill: str,
    word_text: str,
    word_fill: str,
    word_font_family: str,
    letters_font_family: str,
    img_b64_png: str,
    img_x: int,
    img_y: int,
    img_w: int,
    img_h: int,
    letters_x: int,
    letters_y: int,
    word_center_x: int,
    word_y: int,
    letters_font_px: int,
    word_font_px: int,
) -> str:
    """Return an SVG string embedding the illustration and drawing text."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="{canvas_w}" height="{canvas_h}" fill="#FFFFFF"/>
  <image x="{img_x}" y="{img_y}" width="{img_w}" height="{img_h}"
         href="data:image/png;base64,{img_b64_png}" />
  <text x="{letters_x}" y="{letters_y}" fill="{letters_fill}"
        font-family="{letters_font_family}, Andika, DejaVu Sans, Arial, sans-serif"
        font-size="{letters_font_px}" text-anchor="start" dominant-baseline="hanging">{letters_text}</text>
  <text x="{word_center_x}" y="{word_y}" fill="{word_fill}"
        font-family="{word_font_family}, Andika, DejaVu Sans, Arial, sans-serif"
        font-size="{word_font_px}" text-anchor="middle" dominant-baseline="hanging">{word_text}</text>
</svg>
"""

# ----------------------------------
# Build Logic
# ----------------------------------


def build_flashcard_for_pair(
    letter: str,
    word: str,
    illustration_path: Path,
    out_svg_path: Path,
    out_png_path: Path,
    layout: Layout,
    letters_color_rgb: Tuple[int, int, int],
    word_color_rgb: Tuple[int, int, int],
    svg_font_family: str,
    ttf_path: Optional[Path],
    letters_font_override: Optional[int],
    word_font_override: Optional[int],
) -> None:
    """Render both SVG and PNG flashcards for (letter, word)."""
    with Image.open(illustration_path) as src_img:
        src_img = src_img.convert("RGBA")

        # Compute the image area between the letters box and word box, with margins.
        max_w = layout.width - 2 * layout.margin
        top_of_image_area = layout.letters_y + layout.letters_box_h + layout.margin
        bottom_of_image_area = layout.word_y - layout.margin
        available_image_height = bottom_of_image_area - top_of_image_area

        fitted = fit_image(src_img, max_w=max_w, max_h=available_image_height)
        img_w, img_h = fitted.size
        img_x = int((layout.width - img_w) / 2)
        img_y = int(top_of_image_area + (available_image_height - img_h) / 2)

        # Prepare a canvas & draw for text
        canvas = Image.new("RGB", (layout.width, layout.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        # Text content
        letters_text = f"{letter} {letter.lower()}"
        word_text = word

        # Determine fonts (auto-fit or manual override)
        if letters_font_override is not None:
            letters_font = load_font_exact(ttf_path, size=letters_font_override)
            letters_px = letters_font_override
        else:
            letters_font, letters_px = autofit_font(
                text=letters_text,
                max_w=layout.letters_box_w,
                max_h=layout.letters_box_h,
                font_path=ttf_path,
                start_size=32,
                step=4,
            )

        if word_font_override is not None:
            word_font = load_font_exact(ttf_path, size=word_font_override)
            word_px = word_font_override
        else:
            word_font, word_px = autofit_font(
                text=word_text,
                max_w=layout.word_box_w,
                max_h=layout.word_box_h,
                font_path=ttf_path,
                start_size=28,
                step=3,
            )

        # ----- Draw top letters with glyph-top alignment (prevents clipping) -----
        letters_bbox = draw.textbbox((0, 0), letters_text, font=letters_font)
        top_padding = int(0.006 * layout.height)
        letters_draw_y = layout.letters_y + top_padding - letters_bbox[1]
        draw.text(
            (layout.letters_x, letters_draw_y),
            letters_text,
            font=letters_font,
            fill=letters_color_rgb,
        )

        # Paste illustration
        canvas.paste(fitted, (img_x, img_y), fitted)

        # ----- Draw bottom word centered, with glyph-top alignment -----
        word_bbox = draw.textbbox((0, 0), word_text, font=word_font)
        bottom_padding = int(0.006 * layout.height)
        word_top_line = layout.word_y + bottom_padding
        word_draw_y = word_top_line - word_bbox[1]
        # center horizontally
        word_w = word_bbox[2] - word_bbox[0]
        word_x = int(layout.width / 2 - word_w / 2)
        draw.text((word_x, word_draw_y), word_text, font=word_font, fill=word_color_rgb)

        out_png_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(out_png_path, format="PNG")

        # --- SVG with same aligned Ys ---
        b64_png = pil_to_base64_png(fitted)
        svg_text = compose_svg(
            canvas_w=layout.width,
            canvas_h=layout.height,
            letters_text=letters_text,
            letters_fill=rgb_to_hex(letters_color_rgb),
            word_text=word_text,
            word_fill=rgb_to_hex(word_color_rgb),
            word_font_family=svg_font_family,
            letters_font_family=svg_font_family,
            img_b64_png=b64_png,
            img_x=img_x,
            img_y=img_y,
            img_w=img_w,
            img_h=img_h,
            letters_x=layout.letters_x,
            letters_y=letters_draw_y,
            word_center_x=int(layout.width / 2),
            word_y=word_draw_y,
            letters_font_px=letters_px,
            word_font_px=word_px,
        )

        out_svg_path.parent.mkdir(parents=True, exist_ok=True)
        out_svg_path.write_text(svg_text, encoding="utf-8")

# ----------------------------------
# CLI
# ----------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose SVG + PNG flashcards from illustration images.")
    parser.add_argument("--mapping", type=Path, required=True, help="Path to mapping.json")
    parser.add_argument("--images", type=Path, required=True, help="Directory of source illustrations.")
    parser.add_argument("--out", type=Path, required=True, help="Output directory (contains svgs/ and pngs/).")
    parser.add_argument("--width", type=int, default=1500, help="Flashcard width in pixels.")
    parser.add_argument("--height", type=int, default=2500, help="Flashcard height in pixels.")
    parser.add_argument("--font", type=Path, default=None, help="Optional path to a TrueType font file.")
    parser.add_argument("--letter_color", type=str, default="#FF0000", help='Hex color for letters (default: red).')
    parser.add_argument("--word_color", type=str, default="#000000", help='Hex color for words (default: black).')
    parser.add_argument("--svg_font_family", type=str, default="Andika", help="SVG font-family fallback chain.")
    parser.add_argument("--letters_font_size", type=int, default=None, help="Override font size for letters.")
    parser.add_argument("--word_font_size", type=int, default=None, help="Override font size for word.")
    return parser.parse_args()

# ----------------------------------
# Main
# ----------------------------------


def main() -> None:
    args = parse_args()

    pairs = load_mapping(args.mapping)
    svg_dir, png_dir = ensure_out_dirs(args.out)

    # Canvas dimensions are used only for illustration fitting/placement; text auto-fit uses boxes.
    layout = Layout(width=args.width, height=args.height)
    ttf_path = resolve_font_path(args.font)

    letters_color_rgb = hex_to_rgb(args.letter_color)
    word_color_rgb = hex_to_rgb(args.word_color)

    missing: List[str] = []

    for letter, word in pairs:
        illustration = find_illustration(args.images, word)
        base = f"{letter} ({word})"
        out_svg = svg_dir / f"{base}.svg"
        out_png = png_dir / f"{base}.png"

        if illustration is None:
            missing.append(f"{base} — missing illustration for '{word}'")
            continue

        build_flashcard_for_pair(
            letter=letter,
            word=word,
            illustration_path=illustration,
            out_svg_path=out_svg,
            out_png_path=out_png,
            layout=layout,
            letters_color_rgb=letters_color_rgb,
            word_color_rgb=word_color_rgb,
            svg_font_family=args.svg_font_family,
            ttf_path=ttf_path,
            letters_font_override=args.letters_font_size,
            word_font_override=args.word_font_size,
        )

    if missing:
        print("\nSome flashcards were skipped due to missing illustrations:")
        for line in missing:
            print(" -", line)
    else:
        print("✅ All flashcards generated successfully.")


if __name__ == "__main__":
    main()
