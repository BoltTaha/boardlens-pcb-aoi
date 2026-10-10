#!/usr/bin/env python3
"""Fit (memory-bank construction, not gradient training) Anomalib PatchCore."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import shutil
from pathlib import Path

import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--category", choices=["pcb1", "pcb2", "pcb3", "pcb4"], required=True)
    parser.add_argument("--output", type=Path, default=Path("artifacts/models"))
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--coreset-ratio", type=float, default=0.001)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    try:
        import torch
        from anomalib.data import Folder
        from anomalib.engine import Engine
        from anomalib.models import Patchcore
    except ImportError as exc:
        raise SystemExit("Install the ML dependencies with: pip install -e '.[ml]'") from exc
    torch.manual_seed(args.seed)
    category_root = args.data_root / "1cls" / args.category
    if not category_root.exists():
        raise SystemExit(f"Prepared category not found: {category_root}")
    datamodule = Folder(
        name=f"visa-{args.category}",
        root=category_root,
        normal_dir="train/good",
        abnormal_dir="test/bad",
        normal_test_dir="test/good",
        mask_dir="ground_truth/bad",
        train_batch_size=4,
        eval_batch_size=4,
        num_workers=0,
        val_split_mode="none",
        seed=args.seed,
    )
    pre_processor = Patchcore.configure_pre_processor(
        image_size=(args.image_size, args.image_size),
        center_crop_size=(args.image_size, args.image_size),
    )
    model = Patchcore(
        backbone="resnet18",
        layers=["layer2", "layer3"],
        coreset_sampling_ratio=args.coreset_ratio,
        num_neighbors=1,
        pre_processor=pre_processor,
    )
    run_dir = args.output / f"patchcore-{args.category}-v0"
    engine = Engine(
        default_root_dir=run_dir,
        accelerator="cpu",
        devices=1,
        logger=False,
        max_epochs=1,
        enable_progress_bar=True,
        limit_val_batches=0,
        num_sanity_val_steps=0,
    )
    engine.fit(model=model, datamodule=datamodule)
    results = engine.test(model=model, datamodule=datamodule)
    args.output.mkdir(parents=True, exist_ok=True)
    checkpoints = sorted(run_dir.rglob("model.ckpt"), key=lambda path: path.stat().st_mtime)
    if not checkpoints:
        raise RuntimeError("Anomalib fit completed without a checkpoint")
    canonical_checkpoint = args.output / f"patchcore-{args.category}-v0.ckpt"
    if (
        not canonical_checkpoint.exists()
        or canonical_checkpoint.resolve() != checkpoints[-1].resolve()
    ):
        if canonical_checkpoint.is_symlink():
            canonical_checkpoint.unlink()
        shutil.copy2(checkpoints[-1], canonical_checkpoint)
    digest = hashlib.sha256(canonical_checkpoint.read_bytes()).hexdigest()
    metadata = {
        "model_id": f"patchcore-{args.category}-v0",
        "framework": "anomalib",
        "algorithm": "PatchCore",
        "category": args.category,
        "image_size": args.image_size,
        "coreset_ratio": args.coreset_ratio,
        "seed": args.seed,
        "device": "cpu",
        "python": platform.python_version(),
        "torch": torch.__version__,
        "checkpoint": str(canonical_checkpoint),
        "checkpoint_bytes": canonical_checkpoint.stat().st_size,
        "checkpoint_sha256": digest,
        "results": results,
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, default=str))
    print(json.dumps(metadata, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
