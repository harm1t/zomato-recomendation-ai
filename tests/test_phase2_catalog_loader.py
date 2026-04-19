from __future__ import annotations

from pathlib import Path

import pandas as pd

from restaurant_rec.phases.phase2.catalog_loader import load_catalog


def test_load_catalog_explicit_path(tmp_path: Path) -> None:
    p = tmp_path / "r.parquet"
    df = pd.DataFrame(
        [
            {
                "locality": "A",
                "city": "B",
                "cuisines": [["X"]],
                "rating": 4.0,
                "votes": 1,
            }
        ]
    )
    df.to_parquet(p, index=False)
    out = load_catalog(p)
    assert len(out) == 1
    assert out.iloc[0]["locality"] == "A"


def test_load_catalog_missing_raises(tmp_path: Path) -> None:
    try:
        load_catalog(tmp_path / "missing.parquet")
    except FileNotFoundError as e:
        assert "missing.parquet" in str(e)
    else:
        raise AssertionError("expected FileNotFoundError")
