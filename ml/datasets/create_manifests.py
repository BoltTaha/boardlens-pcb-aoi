#!/usr/bin/env python3
"""Filter the official VisA 1-class split into immutable PCB manifests."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

PCB_CATEGORIES = {"pcb1", "pcb2", "pcb3", "pcb4"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("split_csv", type=Path)
    parser.add_argument("output", type=Path, default=Path("data/manifests"), nargs="?")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(args.split_csv.open(newline="")))
    summary: dict[str, dict[str, int]] = {}
    for category in sorted(PCB_CATEGORIES):
        selected = [row for row in rows if row["object"] == category]
        with (args.output / f"visa_1cls_{category}.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(selected)
        counts = Counter(f"{row['split']}:{row['label']}" for row in selected)
        summary[category] = dict(sorted(counts.items()))
    (args.output / "visa_1cls_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
