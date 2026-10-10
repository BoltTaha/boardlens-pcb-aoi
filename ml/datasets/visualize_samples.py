#!/usr/bin/env python3
"""Render deterministic normal/anomaly/mask examples from prepared VisA data."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def first_file(path: Path) -> Path:
    return sorted(item for item in path.iterdir() if item.is_file())[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    tile_size = (360, 280)
    canvas = Image.new("RGB", (tile_size[0] * 3, tile_size[1] * 4), "#07131c")
    draw = ImageDraw.Draw(canvas)
    for row, category in enumerate(("pcb1", "pcb2", "pcb3", "pcb4")):
        root = args.root / "1cls" / category
        anomaly_path = first_file(root / "test" / "bad")
        sources = [
            ("NORMAL", first_file(root / "test" / "good")),
            ("ANOMALY", anomaly_path),
            ("MASK", root / "ground_truth" / "bad" / anomaly_path.name.replace("JPG", "png")),
        ]
        for column, (label, path) in enumerate(sources):
            image = Image.open(path).convert("RGB")
            image.thumbnail((tile_size[0] - 20, tile_size[1] - 38))
            x = column * tile_size[0] + (tile_size[0] - image.width) // 2
            y = row * tile_size[1] + 28
            canvas.paste(image, (x, y))
            draw.text(
                (column * tile_size[0] + 10, row * tile_size[1] + 8),
                f"{category.upper()} · {label}",
                fill="#dce8ee",
                font=ImageFont.load_default(),
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
