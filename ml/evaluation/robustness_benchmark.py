#!/usr/bin/env python3
"""Controlled synthetic robustness benchmark for a fitted PatchCore checkpoint."""

from __future__ import annotations

import argparse
import json
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from torch.utils.data import DataLoader


def variants(image: Image.Image, rng: np.random.Generator) -> dict[str, Image.Image]:
    array = np.asarray(image).astype(np.float32)
    noisy = np.clip(array + rng.normal(0, 12, array.shape), 0, 255).astype(np.uint8)
    misaligned = Image.new("RGB", image.size, "black")
    misaligned.paste(image, (6, -4))
    occluded = image.copy()
    block = Image.new("RGB", (image.width // 8, image.height // 8), "black")
    occluded.paste(block, (image.width // 2, image.height // 2))
    scaled = image.resize((round(image.width * 0.95), round(image.height * 0.95)))
    scaled_canvas = Image.new("RGB", image.size, "black")
    scaled_canvas.paste(
        scaled, ((image.width - scaled.width) // 2, (image.height - scaled.height) // 2)
    )
    return {
        "baseline": image,
        "brightness_070": ImageEnhance.Brightness(image).enhance(0.7),
        "contrast_070": ImageEnhance.Contrast(image).enhance(0.7),
        "gaussian_noise_12": Image.fromarray(noisy),
        "blur_150": image.filter(ImageFilter.GaussianBlur(1.5)),
        "rotate_2deg": image.rotate(2, resample=Image.Resampling.BILINEAR),
        "translate_6m4": misaligned,
        "scale_095": scaled_canvas,
        "partial_occlusion": occluded,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--test-root", type=Path, required=True)
    parser.add_argument("--threshold", type=float, required=True)
    parser.add_argument("--samples-per-class", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from anomalib.data import PredictDataset
    from anomalib.engine import Engine
    from anomalib.models import Patchcore

    rng = np.random.default_rng(42)
    with tempfile.TemporaryDirectory(prefix="boardlens-robustness-") as directory:
        temp = Path(directory)
        selected = [
            *(sorted((args.test_root / "good").glob("*.JPG"))[: args.samples_per_class]),
            *(sorted((args.test_root / "bad").glob("*.JPG"))[: args.samples_per_class]),
        ]
        truth: dict[str, tuple[str, int]] = {}
        for index, path in enumerate(selected):
            label = int(path.parent.name == "bad")
            image = Image.open(path).convert("RGB")
            for variant, transformed in variants(image, rng).items():
                name = f"{variant}__{label}__{index:03d}.png"
                transformed.save(temp / name)
                truth[name] = (variant, label)
        model = Patchcore.load_from_checkpoint(
            args.checkpoint,
            map_location="cpu",
            weights_only=False,
            pre_trained=False,
        )
        dataset = PredictDataset(temp)
        loader = DataLoader(dataset, batch_size=4, collate_fn=dataset.collate_fn, num_workers=0)
        engine = Engine(accelerator="cpu", devices=1, logger=False, enable_progress_bar=True)
        batches = engine.predict(model=model, dataloaders=loader, return_predictions=True)
        grouped: dict[str, list[tuple[int, float]]] = defaultdict(list)
        for batch in batches or []:
            for index, path_string in enumerate(batch.image_path):
                name = Path(path_string).name
                variant, label = truth[name]
                grouped[variant].append((label, float(batch.pred_score[index].detach().cpu())))
    metrics = {}
    for variant, rows in sorted(grouped.items()):
        labels = np.asarray([row[0] for row in rows])
        predicted = np.asarray([row[1] >= args.threshold for row in rows])
        metrics[variant] = {
            "defect_recall": float(np.mean(predicted[labels == 1])),
            "false_positive_rate": float(np.mean(predicted[labels == 0])),
            "samples": len(rows),
        }
    baseline = metrics["baseline"]
    for values in metrics.values():
        values["recall_delta"] = values["defect_recall"] - baseline["defect_recall"]
        values["fpr_delta"] = values["false_positive_rate"] - baseline["false_positive_rate"]
    report = {
        "kind": "controlled_synthetic_robustness",
        "seed": 42,
        "threshold": args.threshold,
        "samples_per_class": args.samples_per_class,
        "metrics": metrics,
        "warning": "Synthetic perturbations do not validate production-camera robustness.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
