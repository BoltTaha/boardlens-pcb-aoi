#!/usr/bin/env python3
"""Convert binary masks to boxes for a clearly labeled binary anomaly localization experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def mask_to_box(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.nonzero(mask > 0)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def yolo_line(box: tuple[int, int, int, int], width: int, height: int) -> str:
    x1, y1, x2, y2 = box
    values = (
        ((x1 + x2) / 2) / width,
        ((y1 + y2) / 2) / height,
        (x2 - x1) / width,
        (y2 - y1) / height,
    )
    return "0 " + " ".join(f"{value:.8f}" for value in values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mask_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for mask_path in sorted(args.mask_dir.glob("*.png")):
        mask = np.asarray(Image.open(mask_path).convert("L"))
        box = mask_to_box(mask)
        text = "" if box is None else yolo_line(box, mask.shape[1], mask.shape[0]) + "\n"
        (args.output_dir / f"{mask_path.stem}.txt").write_text(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
