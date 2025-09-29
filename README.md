# Alphabet Flashcards (SVG + PNG)

[![Code license: MIT](https://img.shields.io/badge/Code%20License-MIT-blue.svg)](LICENSE-CODE.txt)
[![Image license: CC0](https://img.shields.io/badge/Images%20License-CC0-blue.svg)](LICENSE-IMAGES.txt)
[![Font license: OFL](https://img.shields.io/badge/Font%20License-OFL-blue.svg)](LICENSE-FONTS.txt)

![A screenshot of the A, B, and C flashcards arranged next to each other](https://raw.githubusercontent.com/seanthegeek/alphabet-flashcards/refs/heads/main/a-b-c-flashcards-example.webp)

A clean, kid-friendly A–Z flashcard set with pure white backgrounds, big letters, and simple illustrations.

- **SVG** for perfect scaling
- **PNG** for easy printing (3:5 ratio by default)

Almost this entire project was created by interacting with GPT-5, including the illustrations, Python code to generate the PNG and SVG flashcards files, and the project layout. The only parts of the project that are not AI-generated are the font and some of the documentation (this paragraph and the two after it, for example). However, GPT-5 **did** recommend a font based on the requirements I provided.

To be clear, the AI did not generate all of this correctly on the first or even 20th prompt. It was a collaborative effort between myself and GPT-5 that required a lot of clarification from me to get this end result, including image style critiques bug reports, and even getting GPT-5 to admit that it cannot generate SVG images. Still, with the AI I was able to get to this end result in my free time over a couple of days. Which is equally impressive and worrying. I have lots of Python code skills, but no art skills, and I'd never created image layouts using Python before. On one hand, this lets people create new things in record time, on the other hand it cheapens the value of human creativity, which is sad and disturbing.

You can review the full chat using [this link](https://chatgpt.com/share/68d7faa2-3478-800b-94d1-1beb3c95accb).

Anyway, I hope someone finds this useful.

## Licensing

Code: MIT (see `LICENSE-CODE.txt`)

Images: CC0 (see `LICENSE-IMAGES.txt`)

Fonts: OFL (see `LICENSE-FONTS.txt`)

## Layout & Alignment

The flashcards are laid out with three vertically stacked regions:

1. **Top Letters** — “A a” in red, left-aligned.
2. **Illustration** — centered between text regions.
3. **Bottom Word** — the word (e.g., “Apple”) centered horizontally.

### Consistent Sizes

- The **letters** use one common font size across all cards.
- The **word** uses one common font size across all cards.
- These sizes are computed in a pre-pass that finds the largest size that fits in each region for **every** card (then uses the minimum across the set). You can override via CLI:
  - `--letters_font_size` and/or `--word_font_size`.

### Glyph-Centered Alignment (no clipping)

To avoid visual drift from ascenders/descenders:

- **Top letters** and **bottom word** are aligned using the **glyph’s vertical center** (Pillow’s `textbbox`) to the **center line** of their respective text boxes.  
  This keeps “Ball” and “Apple” aligned identically and prevents “J” clipping.
- The **illustration** is auto-cropped (transparent or near-white borders) and **vertically centered** in the space between the two text regions.

### Image Normalization

Some source images included extra white margins. Before fitting:

- We **auto-crop** fully transparent or near-white borders with a small re-padding.
- This makes all illustrations scale to a consistent visual size.

### Font Handling

- **PNGs**: rendered with a real TTF (defaults to `fonts/Andika-Regular.ttf`) for consistent raster output.
- **SVGs**: reference a font family by **name only** (e.g., `Andika, DejaVu Sans, Arial, sans-serif`), without embedding font data.  
  For exact SVG rendering, install the Andika font locally.

#### Installing the Andika locally

This is optional amd only needed for perfect SVG viewing:

- **macOS:** double-click `Andika-Regular.ttf` → *Install Font*
- **Windows:** right-click `Andika-Regular.ttf` → *Install*
- **Linux:** copy to `~/.local/share/fonts/` (user) or `/usr/local/share/fonts/` (system), then run `fc-cache -f -v`.

### Makefile options (examples)

#### Build with defaults (Andika, red letters, black word)

```bash
make dist
```

#### Custom colors and sizes

```bash
make dist LETTER_COLOR=\#0088FF WORD_COLOR=\#111111 LETTERS_FONT_SIZE=230 WORD_FONT_SIZE=160
```

#### Different canvas size

```bash
make images WIDTH=1800 HEIGHT=2700
```
