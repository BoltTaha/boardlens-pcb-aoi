#!/usr/bin/env python3
"""Create evidence visuals directly from VisA images and binary masks."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


GREEN = (18, 117, 72)
INK = (22, 27, 24)
MUTED = (88, 96, 91)
PAPER = (248, 249, 247)
WHITE = (255, 255, 255)
RED = (230, 48, 57)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def mask_binary(mask: Image.Image) -> Image.Image:
    return mask.convert("L").point(lambda value: 255 if value > 127 else 0)


def fit_panel(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, Image.Resampling.LANCZOS)


def visualize_mask(mask: Image.Image) -> Image.Image:
    base = Image.new("RGB", mask.size, (16, 18, 17))
    white = Image.new("RGB", mask.size, WHITE)
    return Image.composite(white, base, mask)


def overlay_defect(image: Image.Image, mask: Image.Image) -> Image.Image:
    original = image.convert("RGB")
    red_layer = Image.new("RGB", original.size, RED)
    translucent = mask.point(lambda value: int(value * 0.58))
    overlay = Image.composite(red_layer, original, translucent)

    expanded = mask.filter(ImageFilter.MaxFilter(11))
    outline = ImageChops.subtract(expanded, mask.filter(ImageFilter.MinFilter(3)))
    outline_layer = Image.new("RGB", original.size, (255, 225, 70))
    return Image.composite(outline_layer, overlay, outline)


def labeled_panel(image: Image.Image, label: str, size: tuple[int, int]) -> Image.Image:
    panel_w, panel_h = size
    label_h = 62
    canvas = Image.new("RGB", (panel_w, panel_h + label_h), WHITE)
    canvas.paste(fit_panel(image, (panel_w, panel_h)), (0, label_h))
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 16), label, fill=INK, font=font(24, bold=True))
    draw.line((0, label_h - 1, panel_w, label_h - 1), fill=(220, 224, 221), width=1)
    return canvas


def create_triptych(name: str, image_path: Path, mask_path: Path, output_dir: Path) -> tuple[Path, float]:
    image = Image.open(image_path).convert("RGB")
    mask = mask_binary(Image.open(mask_path))
    if image.size != mask.size:
        raise ValueError(f"Image/mask size mismatch for {name}: {image.size} vs {mask.size}")

    defect_pixels = sum(mask.histogram()[128:])
    coverage = 100.0 * defect_pixels / (mask.width * mask.height)
    panels = [
        labeled_panel(image, "Original anomaly image", (560, 390)),
        labeled_panel(visualize_mask(mask), "Ground-truth mask", (560, 390)),
        labeled_panel(overlay_defect(image, mask), "Defect overlay", (560, 390)),
    ]

    margin, gap, header_h = 54, 24, 130
    width = margin * 2 + sum(p.width for p in panels) + gap * 2
    height = header_h + panels[0].height + 70
    canvas = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 30), name.upper(), fill=GREEN, font=font(35, bold=True))
    draw.text(
        (margin, 78),
        "White mask pixels are dataset labels; red/yellow shows the same pixels on the source image.",
        fill=MUTED,
        font=font(22),
    )
    x = margin
    for panel in panels:
        canvas.paste(panel, (x, header_h))
        x += panel.width + gap
    draw.text((margin, height - 44), f"Labeled region: {coverage:.3f}% of image pixels", fill=MUTED, font=font(20))

    output = output_dir / f"{name}-ground-truth-evidence.png"
    canvas.save(output, quality=95)
    return output, coverage


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data/processed/visa/1cls"))
    parser.add_argument("--output-dir", type=Path, default=Path("docs/assets/ground-truth"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, Path, float]] = []
    for name in ("pcb1", "pcb2", "pcb3"):
        image_path = args.data_root / name / "test" / "bad" / "000.JPG"
        mask_path = args.data_root / name / "ground_truth" / "bad" / "000.png"
        output, coverage = create_triptych(name, image_path, mask_path, args.output_dir)
        rows.append((name, output, coverage))
        print(f"{name}: {output} ({coverage:.3f}% labeled pixels)")

    previews = [Image.open(path).convert("RGB") for _, path, _ in rows]
    target_w = max(image.width for image in previews)
    resized = [ImageOps.contain(image, (target_w, 570), Image.Resampling.LANCZOS) for image in previews]
    gap = 30
    combined = Image.new("RGB", (target_w, sum(image.height for image in resized) + gap * 2), PAPER)
    y = 0
    for image in resized:
        combined.paste(image, ((target_w - image.width) // 2, y))
        y += image.height + gap
    combined_path = args.output_dir / "visa-pcb-ground-truth-collage.png"
    combined.save(combined_path, quality=95)
    print(f"combined: {combined_path}")


if __name__ == "__main__":
    main()
