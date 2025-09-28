# -----------------------------------------
# Flashcards Makefile
# -----------------------------------------
.PHONY: all images dist clean check fonts-check

# Dimensions for flashcards
WIDTH ?= 1500
HEIGHT ?= 2500

# Font sizes (leave blank for auto-scaling)
LETTERS_FONT_SIZE ?=
WORD_FONT_SIZE ?=

# Font colors (hex values). IMPORTANT: escape leading # so Make doesn't treat it as a comment.
LETTER_COLOR ?= \#FF0000   # red
WORD_COLOR   ?= \#000000   # black

# Font config
# PNGs: Pillow uses a real TTF at FONT_PATH (for consistent raster text)
# SVGs: use family name only; no font is embedded
FONT_PATH       ?= fonts/Andika-Regular.ttf
SVG_FONT_FAMILY ?= Andika

# Core directories
IMAGES_DIR = data/illustrations
OUT_DIR    = data
SVG_DIR    = $(OUT_DIR)/svgs
PNG_DIR    = $(OUT_DIR)/pngs
DIST_DIR   = dist

# Mapping file
MAPPING = mapping.json

# Default target
all: images

fonts-check:
	@if [ ! -f "$(FONT_PATH)" ]; then \
		echo "⚠️  Font not found at $(FONT_PATH). SVGs will still reference '$(SVG_FONT_FAMILY)' by name,"; \
		echo "   but PNGs may fall back to a default font. Consider adding Andika to 'fonts/'."; \
	else \
		echo "✅ Found font: $(FONT_PATH)"; \
	fi

# Generate both SVG and PNG flashcards (SVG font-family: name only; PNG uses FONT_PATH)
images: fonts-check
	@echo ">>> Generating SVG and PNG flashcards (SVG font-family: $(SVG_FONT_FAMILY))..."
	python scripts/compose_flashcards_from_png.py \
		--mapping $(MAPPING) \
		--images $(IMAGES_DIR) \
		--out $(OUT_DIR) \
		--width $(WIDTH) \
		--height $(HEIGHT) \
		--letter_color '$(LETTER_COLOR)' \
	    --word_color '$(WORD_COLOR)' \
		--svg_font_family '$(SVG_FONT_FAMILY)' \
		$(if $(FONT_PATH),--font '$(FONT_PATH)') \
		$(if $(LETTERS_FONT_SIZE),--letters_font_size $(LETTERS_FONT_SIZE)) \
		$(if $(WORD_FONT_SIZE),--word_font_size $(WORD_FONT_SIZE))

# Check for missing or extra files
check:
	@echo ">>> Checking for missing or extra flashcards..."
	python scripts/check_naming.py --mapping $(MAPPING) --svgs $(SVG_DIR) --pngs $(PNG_DIR)

# Build final distribution ZIP files (accept same options as images)
dist: clean
	@echo ">>> Building and packaging final flashcards..."
	$(MAKE) images \
		WIDTH=$(WIDTH) \
		HEIGHT=$(HEIGHT) \
		LETTERS_FONT_SIZE=$(LETTERS_FONT_SIZE) \
		WORD_FONT_SIZE=$(WORD_FONT_SIZE) \
		LETTER_COLOR='$(LETTER_COLOR)' \
		WORD_COLOR='$(WORD_COLOR)' \
		FONT_PATH='$(FONT_PATH)' \
		SVG_FONT_FAMILY='$(SVG_FONT_FAMILY)'
	mkdir -p $(DIST_DIR)
	zip -j -r $(DIST_DIR)/flashcards_svgs.zip $(SVG_DIR)
	zip -j -r $(DIST_DIR)/flashcards_pngs.zip $(PNG_DIR)
	@echo ">>> Done! ZIP files are now in '$(DIST_DIR)' directory."

# Clean build artifacts
clean:
	@echo ">>> Cleaning generated files..."
	rm -rf $(SVG_DIR) $(PNG_DIR) $(DIST_DIR)
