# Contributing

## Ways to contribute

- Improve scripts or layout
- Provide higher-quality illustrations (object-only, white background)
- Add localized word sets (e.g., Spanish, French)

## Guidelines

- Keep backgrounds **pure white** (#FFFFFF)
- No text inside source illustrations
- Realistic animal colors; bright but simple objects

## Dev setup

### Install dependencies

#### macOS (Homebrew)

1. Install [Homebrew](https://brew.sh/)
2. Run `brew update && brew install cairo pango gdk-pixbuf libffi pkg-config`

#### Debian or Ubuntu Linux

```bash
sudo apt update && sudo apt install -y  make libcairo2 libcairo2-dev libpango1.0-dev libgdk-pixbuf2.0-dev libffi-dev pkg-config python3-venv
```

#### RHEL-based Linux (Fedora, CentOS, Rocky, etc.)

```bash
sudo dnf install -y make cairo cairo-devel pango pango-devel gdk-pixbuf2 gdk-pixbuf2-devel libffi libffi-devel pkg-config python3-venv
```

For CentOS 7 or older, replace `dnf` with `yum`.

#### Windows

Use the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) to install a Linux distribution, then follow the instructions above.

### Create the Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
