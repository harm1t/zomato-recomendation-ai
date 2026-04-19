#!/usr/bin/env python3
"""Build ``data/processed/restaurants.parquet`` from the Hugging Face Zomato dataset."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_src_on_path() -> Path:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    return root


def main() -> None:
    root = _ensure_src_on_path()
    from restaurant_rec.phases.phase1.ingest import run_ingest

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default=None,
        help="Path to config.yaml (default: <project>/config.yaml)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Override output Parquet path (default: paths.processed_catalog in config)",
    )
    args = parser.parse_args()

    stats = run_ingest(
        config_path=args.config,
        project_root=root,
        output_path=args.output,
    )
    for line in stats.summary_lines():
        print(line)


if __name__ == "__main__":
    main()
