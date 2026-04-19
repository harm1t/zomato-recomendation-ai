from __future__ import annotations

import json

import pandas as pd

from restaurant_rec.core.config import AppConfig, FilterConfig, GeminiConfig
from restaurant_rec.phases.phase2.preferences import UserPreferences
from restaurant_rec.phases.phase3.orchestration import recommend


def _catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "r1",
                "name": "Spice Hub",
                "locality": "Indiranagar",
                "city": "Bangalore",
                "cuisines": ["North Indian"],
                "rating": 4.2,
                "cost_for_two": 600,
                "votes": 50,
                "budget_tier": "medium",
                "raw_features": "",
            },
            {
                "id": "r2",
                "name": "Dragon",
                "locality": "Indiranagar",
                "city": "Bangalore",
                "cuisines": ["Chinese"],
                "rating": 4.0,
                "cost_for_two": 400,
                "votes": 30,
                "budget_tier": "low",
                "raw_features": "",
            },
        ]
    )


def test_recommend_empty_filter() -> None:
    cfg = AppConfig(
        filter=FilterConfig(max_shortlist_candidates=10),
        gemini=GeminiConfig(top_k_recommendations=3),
    )
    prefs = UserPreferences(location="NowhereCity", min_rating=0.0)
    res = recommend(_catalog(), prefs, cfg=cfg)
    assert res.items == []
    assert "No restaurants matched" in res.summary
    assert res.meta.used_llm is False


def test_recommend_mock_llm() -> None:
    cfg = AppConfig(
        filter=FilterConfig(max_shortlist_candidates=10),
        gemini=GeminiConfig(top_k_recommendations=5, prompt_version="vtest"),
    )
    prefs = UserPreferences(location="Indiranagar", min_rating=0.0)

    def fake_llm(system: str, user: str) -> str:
        assert "restaurant_id" in user
        return json.dumps(
            {
                "summary": "Great picks",
                "recommendations": [
                    {"restaurant_id": "r2", "rank": 1, "explanation": "Budget-friendly Chinese."},
                    {"restaurant_id": "r1", "rank": 2, "explanation": "Highly rated North Indian."},
                ],
            }
        )

    res = recommend(_catalog(), prefs, cfg=cfg, generate_fn=fake_llm)
    assert res.meta.used_llm is True
    assert res.meta.parse_fallback is False
    assert res.summary == "Great picks"
    assert len(res.items) == 2
    assert res.items[0]["id"] == "r2"
    assert res.items[0]["explanation"] == "Budget-friendly Chinese."
    assert "₹" in res.items[0]["cost_display"]


def test_recommend_parse_fallback_with_mock() -> None:
    cfg = AppConfig(
        filter=FilterConfig(max_shortlist_candidates=10),
        gemini=GeminiConfig(top_k_recommendations=1),
    )
    prefs = UserPreferences(location="Indiranagar", min_rating=0.0)

    def bad_llm(system: str, user: str) -> str:
        return "NOT JSON"

    res = recommend(_catalog(), prefs, cfg=cfg, generate_fn=bad_llm)
    assert res.meta.used_llm is True
    assert res.meta.parse_fallback is True
    assert len(res.items) >= 1
    assert "catalog shortlist" in res.items[0]["explanation"].lower()
