# Alphabet Flashcards (SVG + PNG)

[![License: MIT](https://img.shields.io/badge/Code%20License-MIT-green.svg)](LICENSE-CODE.md)
[![License: CC0](https://img.shields.io/badge/Images%20License-CC0-blue.svg)](LICENSE-IMAGES.md)

A clean, kid-friendly A–Z flashcard set with pure white backgrounds, big letters, and simple illustrations.

- **SVG** for perfect scaling
- **PNG** for easy printing (3:5 ratio by default)

Almost this entire project was created by interacting with GPT-5, including the illustrations, Python code to generate the PNG and SVG flashcards files, and the project layout. The only parts of the project that are not AI-generated are the font and some of the documentation (this paragraph and the two after it, for example). However, GPT-5 **did** recommend a font based on the requirements I provided.

To be clear, the AI did not generate all of this correctly on the first or even 20th prompt. It was a collaborative effort between myself and GPT-5 that required a lot of clarification from me to get this end result, including image style critiques bug reports, and even getting GPT-5 to admit that it cannot generate SVG images. Still, with the AI I was able to get to this end result in my free time over a couple of days. Which is equally impressive and worrying. I have lots of Python code skills, but no art skills, and I'd never done image generation before. On one hand, this lets people create new things in record time, on the other hand it cheapens the value of human creativity, which is sad and disturbing.

You can review the full chat using [this link](https://chatgpt.com/share/68d7faa2-3478-800b-94d1-1beb3c95accb).

Anyway, I hope someone finds this useful.

## Licensing

Code: MIT (see `LICENSE-CODE.txt`)

Images: CC0 (see `LICENSE-IMAGES.txt`)

Fonts: OFL (see `LICENSE-FONTS.txt`)

## Fonts

This project references the **Andika** font for SVGs by name only (no embedding),
and uses the TTF file for PNG rendering to ensure consistent raster output.

- Font file (recommended to include in repo): `fonts/Andika-Regular.ttf`
- License: **SIL Open Font License (OFL)** — you may use, modify, and redistribute the font with the project; you may not sell the font by itself.

### SVG behavior  

SVGs reference `font-family: Andika` without embedding the font. To see the exact intended shapes when opening SVGs, install Andika locally or ensure your system has it available. PNGs are unaffected because they are rasterized with the TTF file included in this repository.

### Installing Andika locally

This is optional amd only needed for perfect SVG viewing:

- **macOS:** double-click `Andika-Regular.ttf` → *Install Font*
- **Windows:** right-click `Andika-Regular.ttf` → *Install*
- **Linux:** copy to `~/.local/share/fonts/` (user) or `/usr/local/share/fonts/` (system), then run `fc-cache -f -v`.

## Contributing

See `CONTRIBUTING.md`.
