#!/usr/bin/env python3
"""Calibrate image thresholds on a deterministic split and evaluate the held-out half."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score
from torch.utils.data import DataLoader


def choose_threshold(normal: np.ndarray, anomaly: np.ndarray, target_recall: float) -> float:
    candidates = np.unique(np.concatenate([normal, anomaly]))
    feasible: list[tuple[float, float]] = []
    for threshold in candidates:
        recall = float(np.mean(anomaly >= threshold))
        false_positive_rate = float(np.mean(normal >= threshold))
        if recall >= target_recall:
            feasible.append((false_positive_rate, -float(threshold)))
    if not feasible:
        raise RuntimeError("No threshold satisfies target recall")
    _, negative_threshold = min(feasible)
    return -negative_threshold


def mask_for(image_path: Path, map_shape: tuple[int, int]) -> np.ndarray:
    if image_path.parent.name == "good":
        return np.zeros(map_shape, dtype=np.uint8)
    mask_path = image_path.parents[2] / "ground_truth" / "bad" / f"{image_path.stem}.png"
    mask = Image.open(mask_path).convert("L").resize(map_shape[::-1], Image.Resampling.NEAREST)
    return (np.asarray(mask) > 0).astype(np.uint8)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--test-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-recall", type=float, default=0.95)
    args = parser.parse_args()

    from anomalib.data import PredictDataset
    from anomalib.engine import Engine
    from anomalib.models import Patchcore

    model = Patchcore.load_from_checkpoint(
        args.checkpoint,
        map_location="cpu",
        weights_only=False,
        pre_trained=False,
    )
    dataset = PredictDataset(args.test_root)
    loader = DataLoader(dataset, batch_size=4, collate_fn=dataset.collate_fn, num_workers=0)
    engine = Engine(accelerator="cpu", devices=1, logger=False, enable_progress_bar=True)
    batches = engine.predict(model=model, dataloaders=loader, return_predictions=True)
    records = []
    for batch in batches or []:
        for index, path_string in enumerate(batch.image_path):
            image_path = Path(path_string)
            anomaly_map = batch.anomaly_map[index].detach().cpu().numpy()
            records.append(
                {
                    "path": str(image_path),
                    "label": int(image_path.parent.name == "bad"),
                    "score": float(batch.pred_score[index].detach().cpu()),
                    "map": anomaly_map,
                    "mask": mask_for(image_path, anomaly_map.shape),
                }
            )
    normal = sorted((record for record in records if not record["label"]), key=lambda x: x["path"])
    anomaly = sorted((record for record in records if record["label"]), key=lambda x: x["path"])
    normal_val, normal_test = normal[::2], normal[1::2]
    anomaly_val, anomaly_test = anomaly[::2], anomaly[1::2]
    fail_threshold = choose_threshold(
        np.asarray([row["score"] for row in normal_val]),
        np.asarray([row["score"] for row in anomaly_val]),
        args.target_recall,
    )
    review_threshold = min(
        choose_threshold(
            np.asarray([row["score"] for row in normal_val]),
            np.asarray([row["score"] for row in anomaly_val]),
            min(0.99, args.target_recall + 0.04),
        ),
        fail_threshold,
    )
    heldout = normal_test + anomaly_test
    labels = np.asarray([row["label"] for row in heldout])
    scores = np.asarray([row["score"] for row in heldout])
    predictions = (scores >= fail_threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
    pixel_labels = np.concatenate([row["mask"].ravel() for row in heldout])
    pixel_scores = np.concatenate([row["map"].ravel() for row in heldout])
    report = {
        "checkpoint": str(args.checkpoint.resolve()),
        "protocol": "sorted even indices calibration; odd indices held out",
        "validation": {"normal": len(normal_val), "anomaly": len(anomaly_val)},
        "heldout": {"normal": len(normal_test), "anomaly": len(anomaly_test)},
        "target_recall": args.target_recall,
        "review_target_recall": min(0.99, args.target_recall + 0.04),
        "thresholds": {"review": review_threshold, "fail": fail_threshold},
        "metrics": {
            "image_auroc": float(roc_auc_score(labels, scores)),
            "defect_recall": tp / (tp + fn),
            "false_positive_rate": fp / (fp + tn),
            "false_negative_rate": fn / (fn + tp),
            "precision": tp / (tp + fp) if tp + fp else 0.0,
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
            "pixel_auroc": float(roc_auc_score(pixel_labels, pixel_scores)),
            "pixel_average_precision": float(average_precision_score(pixel_labels, pixel_scores)),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
