"""Smoke tests against the real Phase 1 artifact when present."""

from __future__ import annotations

from pathlib import Path

import pytest

_CATALOG = Path(__file__).resolve().parents[1] / "data" / "processed" / "restaurants.parquet"


@pytest.mark.skipif(not _CATALOG.is_file(), reason="run scripts/ingest_zomato.py first")
def test_filter_real_catalog_smoke() -> None:
    from restaurant_rec.phases.phase2 import UserPreferences, filter_restaurants, load_catalog

    df = load_catalog(_CATALOG)
    loc = str(df.iloc[0]["locality"] or df.iloc[0]["city"])
    prefs = UserPreferences(location=loc, min_rating=0.0)
    res = filter_restaurants(df, prefs)
    assert res.empty_reason is None
    assert len(res.shortlist) >= 1
