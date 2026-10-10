#!/usr/bin/env python3
"""Generic staged latency reporter for inference adapters."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from PIL import Image


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * q)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts/results/latency.json"))
    args = parser.parse_args()
    files = sorted(
        [*args.images.glob("*.png"), *args.images.glob("*.jpg"), *args.images.glob("*.JPG")]
    )
    if not files:
        raise SystemExit("No images found")
    decode = []
    for path in files:
        start = time.perf_counter()
        with Image.open(path) as image:
            image.convert("RGB").load()
        decode.append((time.perf_counter() - start) * 1000)
    report = {
        "samples": len(files),
        "note": "Decode-only until a genuine model adapter is installed; no inference claim.",
        "decode_ms": {
            "mean": statistics.mean(decode),
            "p50": percentile(decode, 0.5),
            "p95": percentile(decode, 0.95),
            "p99": percentile(decode, 0.99),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
