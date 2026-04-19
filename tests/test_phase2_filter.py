from __future__ import annotations

import pandas as pd

from restaurant_rec.core.config import AppConfig, FilterConfig
from restaurant_rec.phases.phase2.filter import (
    distinct_cities,
    distinct_localities,
    filter_restaurants,
)
from restaurant_rec.phases.phase2.preferences import UserPreferences


def _sample_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "a",
                "name": "R1",
                "locality": "Indiranagar",
                "city": "Bangalore",
                "cuisines": ["Chinese", "Thai"],
                "rating": 4.2,
                "cost_for_two": 500,
                "votes": 10,
                "raw_features": "",
            },
            {
                "id": "b",
                "name": "R2",
                "locality": "Indiranagar",
                "city": "Bangalore",
                "cuisines": ["Italian"],
                "rating": 3.8,
                "cost_for_two": 1200,
                "votes": 5,
                "raw_features": "",
            },
            {
                "id": "c",
                "name": "R3",
                "locality": "Koramangala",
                "city": "Bangalore",
                "cuisines": ["Chinese"],
                "rating": 4.5,
                "cost_for_two": 300,
                "votes": 20,
                "raw_features": "",
            },
        ]
    )


def test_filter_location_and_cuisine() -> None:
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=10))
    prefs = UserPreferences(location="Indiranagar", cuisine="Chinese", min_rating=0.0)
    res = filter_restaurants(_sample_catalog(), prefs, cfg=cfg)
    assert res.empty_reason is None
    assert len(res.shortlist) == 1
    assert res.shortlist.iloc[0]["id"] == "a"
    assert res.counts.after_location == 2


def test_filter_matches_city_column() -> None:
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=10))
    prefs = UserPreferences(location="bangalore", min_rating=0.0)
    res = filter_restaurants(_sample_catalog(), prefs, cfg=cfg)
    assert res.empty_reason is None
    assert len(res.shortlist) == 3


def test_filter_budget() -> None:
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=10))
    prefs = UserPreferences(
        location="Bangalore",
        cuisine="Chinese",
        budget_max_inr=400,
        min_rating=0.0,
    )
    res = filter_restaurants(_sample_catalog(), prefs, cfg=cfg)
    assert res.empty_reason is None
    assert set(res.shortlist["id"].tolist()) == {"c"}
    
    prefs_min = UserPreferences(
        location="Bangalore",
        budget_min_inr=500,
        min_rating=0.0,
    )
    res_min = filter_restaurants(_sample_catalog(), prefs_min, cfg=cfg)
    assert res_min.empty_reason is None
    assert set(res_min.shortlist["id"].tolist()) == {"a", "b"}

    prefs_range = UserPreferences(
        location="Bangalore",
        budget_min_inr=400,
        budget_max_inr=600,
        min_rating=0.0,
    )
    res_range = filter_restaurants(_sample_catalog(), prefs_range, cfg=cfg)
    assert res_range.empty_reason is None
    assert set(res_range.shortlist["id"].tolist()) == {"a"}


def test_filter_no_location() -> None:
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=10))
    prefs = UserPreferences(location="Delhi", min_rating=0.0)
    res = filter_restaurants(_sample_catalog(), prefs, cfg=cfg)
    assert res.empty_reason == "NO_LOCATION"
    assert len(res.shortlist) == 0


def test_filter_no_cuisine() -> None:
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=10))
    prefs = UserPreferences(location="Indiranagar", cuisine="Mexican", min_rating=0.0)
    res = filter_restaurants(_sample_catalog(), prefs, cfg=cfg)
    assert res.empty_reason == "NO_CUISINE"
    assert len(res.shortlist) == 0


def test_filter_min_rating() -> None:
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=10))
    prefs = UserPreferences(location="Bangalore", min_rating=4.4)
    res = filter_restaurants(_sample_catalog(), prefs, cfg=cfg)
    assert res.empty_reason is None
    assert res.shortlist.iloc[0]["id"] == "c"


def test_filter_no_rating() -> None:
    df = _sample_catalog()
    df.loc[0, "rating"] = float("nan")
    df.loc[1, "rating"] = float("nan")
    df.loc[2, "rating"] = float("nan")
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=10))
    prefs = UserPreferences(location="Bangalore", min_rating=3.0)
    res = filter_restaurants(df, prefs, cfg=cfg)
    assert res.empty_reason == "NO_RATING"


def test_filter_cap_shortlist() -> None:
    rows = []
    for i in range(50):
        rows.append(
            {
                "id": str(i),
                "name": f"N{i}",
                "locality": "L",
                "city": "Bangalore",
                "cuisines": ["X"],
                "rating": 4.0,
                "cost_for_two": 100,
                "votes": i,
                "raw_features": "",
            }
        )
    df = pd.DataFrame(rows)
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=5))
    prefs = UserPreferences(location="Bangalore", min_rating=0.0)
    res = filter_restaurants(df, prefs, cfg=cfg)
    assert len(res.shortlist) == 5


def test_relax_min_rating() -> None:
    cfg = AppConfig(filter=FilterConfig(max_shortlist_candidates=10, relax_min_rating=True))
    prefs = UserPreferences(location="Indiranagar", cuisine="Italian", min_rating=4.0)
    res = filter_restaurants(_sample_catalog(), prefs, cfg=cfg)
    assert res.rating_relaxed is True
    assert res.min_rating_effective == 3.5
    assert res.empty_reason is None
    assert len(res.shortlist) == 1
    assert res.shortlist.iloc[0]["id"] == "b"


def test_distinct_localities_and_cities() -> None:
    df = _sample_catalog()
    assert "Indiranagar" in distinct_localities(df)
    assert "Bangalore" in distinct_cities(df)
