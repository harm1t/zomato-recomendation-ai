"""Load Hugging Face Zomato data, transform, validate, write Parquet catalog."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd
from datasets import load_dataset

from restaurant_rec.core.config import AppConfig, load_config, repo_root
from restaurant_rec.phases.phase1.transform import hf_row_to_canonical
from restaurant_rec.phases.phase1.validate import validation_reason


def _dedupe_by_id(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """Keep one row per ``id`` (higher ``votes``, then higher ``rating`` wins)."""
    best: dict[str, dict[str, Any]] = {}
    for r in records:
        rid = r["id"]
        if rid not in best:
            best[rid] = r
            continue
        o = best[rid]
        rv, ov = int(r.get("votes") or 0), int(o.get("votes") or 0)
        if rv > ov:
            best[rid] = r
        elif rv == ov:
            rr = float(r["rating"]) if r.get("rating") is not None else -1.0
            o_r = float(o["rating"]) if o.get("rating") is not None else -1.0
            if rr > o_r:
                best[rid] = r
    merged = list(best.values())
    return merged, len(records) - len(merged)


@dataclass
class IngestStats:
    rows_in: int = 0
    rows_out: int = 0
    drop_counts: Counter[str] = field(default_factory=Counter)
    duplicates_merged: int = 0
    output_path: str = ""

    def summary_lines(self) -> list[str]:
        lines = [
            f"rows_in={self.rows_in}",
            f"rows_out={self.rows_out}",
            f"output={self.output_path}",
        ]
        if self.duplicates_merged:
            lines.append(f"duplicates_merged={self.duplicates_merged}")
        if self.drop_counts:
            lines.append("drops:")
            for reason, n in sorted(self.drop_counts.items(), key=lambda x: (-x[1], x[0])):
                lines.append(f"  {reason}: {n}")
        return lines


def _rows_from_hf(cfg: AppConfig) -> list[dict[str, Any]]:
    ds = load_dataset(cfg.dataset.hf_name, split=cfg.dataset.split)
    return [dict(ds[i]) for i in range(len(ds))]


def build_catalog_records(
    hf_rows: list[dict[str, Any]],
    cfg: AppConfig,
) -> tuple[list[dict[str, Any]], IngestStats]:
    stats = IngestStats()
    stats.rows_in = len(hf_rows)
    kept: list[dict[str, Any]] = []
    for raw in hf_rows:
        row = hf_row_to_canonical(raw, cfg)
        reason = validation_reason(row)
        if reason:
            stats.drop_counts[reason] += 1
            continue
        kept.append(row)
    kept, merged = _dedupe_by_id(kept)
    stats.duplicates_merged = merged
    stats.rows_out = len(kept)
    return kept, stats


def run_ingest(
    config_path: Path | str | None = None,
    project_root: Path | None = None,
    output_path: Path | str | None = None,
) -> IngestStats:
    """
    Download/load HF dataset, transform to canonical schema, write Parquet.

    If ``output_path`` is set, it overrides ``config.paths.processed_catalog``
    (still resolved relative to ``project_root`` when not absolute).
    """
    cfg = load_config(config_path)
    root = project_root or repo_root()
    if output_path is not None:
        out = Path(output_path)
        dest = out if out.is_absolute() else (root / out).resolve()
    else:
        dest = cfg.resolved_processed_catalog(project_root=root)

    dest.parent.mkdir(parents=True, exist_ok=True)

    hf_rows = _rows_from_hf(cfg)
    records, stats = build_catalog_records(hf_rows, cfg)
    stats.output_path = str(dest)

    df = pd.DataFrame.from_records(records)
    df["cost_for_two"] = df["cost_for_two"].astype(pd.Int64Dtype())
    df.to_parquet(dest, index=False)

    return stats
