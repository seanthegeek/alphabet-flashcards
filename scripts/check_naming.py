#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--svgs", default="data/svgs")
    ap.add_argument("--pngs", default="data/pngs")
    ap.add_argument("--mapping", default="mapping.json")
    args = ap.parse_args()

    mapping = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    expected = [f"{k} ({v})" for k, v in mapping.items()]

    def list_base_names(folder: Path, ext: str):
        if not folder.exists():
            return set()
        return {p.stem for p in folder.glob(f"*.{ext}")}

    svgs = list_base_names(Path(args.svgs), "svg")
    pngs = list_base_names(Path(args.pngs), "png")
    exp = set(expected)

    missing_svgs = exp - svgs
    missing_pngs = exp - pngs
    extra_svgs = svgs - exp
    extra_pngs = pngs - exp

    print(f"Expected total: {len(exp)}")
    print(f"SVGs present: {len(svgs)}, PNGs present: {len(pngs)}")

    if missing_svgs:
        print("\nMissing SVGs:")
    for x in sorted(missing_svgs):
        print(" -", x)

    if missing_pngs:
        print("\nMissing PNGs:")
        for x in sorted(missing_pngs):
            print(" -", x)

    if extra_svgs:
        print("\nUnexpected SVGs:")
        for x in sorted(extra_svgs):
            print(" -", x)

    if extra_pngs:
        print("\nUnexpected PNGs:")
        for x in sorted(extra_pngs):
            print(" -", x)


    if not (missing_svgs or missing_pngs or extra_svgs or extra_pngs):
        print("\n✅ All filenames match mapping.json")

if __name__ == "__main__":
    main()
