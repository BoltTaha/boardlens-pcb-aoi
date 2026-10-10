#!/usr/bin/env python3
"""Benchmark warm BoardLens API inspection latency through the in-process ASGI boundary."""

from __future__ import annotations

import argparse
import asyncio
import json
import platform
import resource
import statistics
import time
from pathlib import Path

import httpx
import numpy as np
from boardlens.db.base import init_db
from boardlens.main import app


def summary(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.mean(values),
        "p50": float(np.percentile(values, 50)),
        "p95": float(np.percentile(values, 95)),
        "p99": float(np.percentile(values, 99)),
    }


async def run(args: argparse.Namespace) -> dict:
    images = sorted((args.data_root / "good").glob("*.JPG"))[: args.runs]
    images += sorted((args.data_root / "bad").glob("*.JPG"))[: args.runs]
    if not images:
        raise RuntimeError("No benchmark images found")
    transport = httpx.ASGITransport(app=app)
    wall_times: list[float] = []
    model_times: list[float] = []
    init_db()
    async with httpx.AsyncClient(transport=transport, base_url="http://benchmark") as client:
        sequence = [images[index % len(images)] for index in range(args.warmup + args.runs)]
        for index, path in enumerate(sequence):
            start = time.perf_counter()
            response = await client.post(
                "/inspections",
                data={"product": args.product},
                files={"file": (path.name, path.read_bytes(), "image/jpeg")},
            )
            elapsed = (time.perf_counter() - start) * 1000
            response.raise_for_status()
            if index >= args.warmup:
                wall_times.append(elapsed)
                model_times.append(response.json()["latency_ms"])
    return {
        "hardware": platform.platform(),
        "python": platform.python_version(),
        "product": args.product,
        "samples": args.runs,
        "warmup": args.warmup,
        "batch_size": 1,
        "input_resolution": 224,
        "backend": "PyTorch CPU via Anomalib Engine",
        "wall_ms": summary(wall_times),
        "orchestrator_model_ms": summary(model_times),
        "peak_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        "gpu_memory_mb": None,
        "note": (
            "In-process ASGI; wall time includes validation, artifact writes, inference, "
            "overlay, and SQLite persistence. It excludes network transport."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--product", default="pcb1")
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = asyncio.run(run(args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
