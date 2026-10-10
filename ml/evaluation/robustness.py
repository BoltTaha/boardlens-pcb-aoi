#!/usr/bin/env python3
"""Generate deterministic controlled perturbations; evaluation remains separate."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    image = Image.open(args.image).convert("RGB")
    variants = {
        "brightness_070": ImageEnhance.Brightness(image).enhance(0.7),
        "brightness_130": ImageEnhance.Brightness(image).enhance(1.3),
        "contrast_070": ImageEnhance.Contrast(image).enhance(0.7),
        "blur_150": image.filter(ImageFilter.GaussianBlur(1.5)),
        "rotate_2deg": image.rotate(2, resample=Image.Resampling.BILINEAR),
        "scale_095": image.resize((round(image.width * 0.95), round(image.height * 0.95))),
    }
    for name, value in variants.items():
        value.save(args.output / f"{args.image.stem}_{name}.png")
    print(f"wrote {len(variants)} controlled synthetic variants to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
