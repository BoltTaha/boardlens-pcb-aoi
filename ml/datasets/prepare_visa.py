#!/usr/bin/env python3
"""Create MVTec-style VisA data using the official 1-class split utility."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=Path("third_party/visa_dataset"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/visa"))
    args = parser.parse_args()
    script = args.repo / "utils" / "prepare_data.py"
    split = args.repo / "split_csv" / "1cls.csv"
    if not script.exists() or not split.exists():
        raise SystemExit(
            "Official visa_dataset repository is missing; run scripts/bootstrap_data.sh"
        )
    command = [
        "python3",
        str(script),
        "--split-type",
        "1cls",
        "--data-folder",
        str(args.source),
        "--save-folder",
        str(args.output),
        "--split-file",
        str(split),
    ]
    return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
