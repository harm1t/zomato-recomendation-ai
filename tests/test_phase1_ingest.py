from __future__ import annotations

from restaurant_rec.core.config import AppConfig, BudgetTiersConfig, RatingConfig
from restaurant_rec.phases.phase1.ingest import _dedupe_by_id, build_catalog_records


def _cfg() -> AppConfig:
    return AppConfig(
        budget_tiers=BudgetTiersConfig(low_max_inr=400, medium_max_inr=800),
        rating=RatingConfig(),
    )


def test_dedupe_prefers_higher_votes() -> None:
    a = {"id": "x", "votes": 1, "rating": 4.0}
    b = {"id": "x", "votes": 10, "rating": 3.0}
    out, merged = _dedupe_by_id([a, b])
    assert merged == 1
    assert len(out) == 1
    assert out[0]["votes"] == 10


def test_build_catalog_drops_and_counts() -> None:
    cfg = _cfg()
    hf_rows = [
        {
            "name": "",
            "location": "L",
            "listed_in(city)": "C",
            "cuisines": "X",
            "rate": "4/5",
            "votes": 1,
            "approx_cost(for two people)": "100",
            "address": "",
            "url": "http://a",
        },
        {
            "name": "Good",
            "location": "L",
            "listed_in(city)": "C",
            "cuisines": "X",
            "rate": "4/5",
            "votes": 2,
            "approx_cost(for two people)": "100",
            "address": "",
            "url": "http://b",
        },
    ]
    records, stats = build_catalog_records(hf_rows, cfg)
    assert stats.rows_in == 2
    assert stats.drop_counts["MISSING_NAME"] == 1
    assert len(records) == 1
    assert records[0]["name"] == "Good"
