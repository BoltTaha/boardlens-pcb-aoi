#!/usr/bin/env python3
"""Validate original or MVTec-formatted VisA PCB subsets without modifying source data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from PIL import Image

PCB_CATEGORIES = ("pcb1", "pcb2", "pcb3", "pcb4")


def sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def image_metadata(path: Path) -> dict:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
        }


def validate_original(root: Path, categories: tuple[str, ...]) -> dict:
    report: dict = {
        "layout": "original",
        "root": str(root.resolve()),
        "categories": {},
        "errors": [],
    }
    for category in categories:
        category_root = root / category
        csv_path = category_root / "image_anno.csv"
        if not csv_path.exists():
            report["errors"].append(f"missing {csv_path}")
            continue
        rows = list(csv.DictReader(csv_path.open(newline="")))
        counts = Counter()
        sizes = Counter()
        modes = Counter()
        missing: list[str] = []
        corrupt: list[str] = []
        mask_values = Counter()
        for row in rows:
            image_rel = row.get("image") or row.get("image_path")
            if not image_rel:
                corrupt.append("annotation row has no image field")
                continue
            image_path = root / image_rel
            if not image_path.exists():
                missing.append(str(image_path))
                continue
            try:
                meta = image_metadata(image_path)
                sizes[f"{meta['width']}x{meta['height']}"] += 1
                modes[meta["mode"]] += 1
            except Exception as exc:  # report all damaged inputs in one run
                corrupt.append(f"{image_path}: {exc}")
            label = (row.get("label") or row.get("anomaly_class") or "unknown").strip().lower()
            counts[label] += 1
            mask_rel = row.get("mask") or row.get("mask_path")
            if mask_rel and mask_rel.strip():
                mask_path = root / mask_rel
                if not mask_path.exists():
                    missing.append(str(mask_path))
                else:
                    try:
                        with Image.open(mask_path) as mask:
                            mask_values.update(mask.getdata())
                    except Exception as exc:
                        corrupt.append(f"{mask_path}: {exc}")
        report["categories"][category] = {
            "annotations": len(rows),
            "labels": dict(counts),
            "image_sizes": dict(sizes),
            "modes": dict(modes),
            "mask_pixel_values": sorted(mask_values),
            "missing_count": len(missing),
            "corrupt_count": len(corrupt),
            "missing_examples": missing[:20],
            "corrupt_examples": corrupt[:20],
            "annotation_sha256": sha256(csv_path),
        }
    report["valid"] = not report["errors"] and all(
        not value["missing_count"] and not value["corrupt_count"]
        for value in report["categories"].values()
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--categories", nargs="+", default=list(PCB_CATEGORIES))
    parser.add_argument("--output", type=Path, default=Path("artifacts/results/dataset-audit.json"))
    args = parser.parse_args()
    report = validate_original(args.root, tuple(args.categories))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
