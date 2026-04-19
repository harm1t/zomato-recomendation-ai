"""Phase 4 FastAPI tests (no live Gemini — ``generate_fn`` stub)."""

from __future__ import annotations

import json

import pandas as pd
from fastapi.testclient import TestClient

from restaurant_rec.core.config import AppConfig, FilterConfig, GeminiConfig
from restaurant_rec.phases.phase4.app import create_app


def _tiny_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": "api-t1",
                "name": "API Test Bistro",
                "locality": "ApiTestVille",
                "city": "ApiTestCity",
                "cuisines": ["Italian"],
                "rating": 4.3,
                "cost_for_two": 900,
                "votes": 100,
                "budget_tier": "medium",
                "address": "",
                "url": "https://example.com/api-t1",
                "raw_features": "",
            },
            {
                "id": "api-t2",
                "name": "API Test Dosa",
                "locality": "ApiTestVille",
                "city": "ApiTestCity",
                "cuisines": ["South Indian"],
                "rating": 4.1,
                "cost_for_two": 350,
                "votes": 80,
                "budget_tier": "low",
                "address": "",
                "url": "https://example.com/api-t2",
                "raw_features": "",
            },
        ]
    )


def _cfg() -> AppConfig:
    return AppConfig(
        filter=FilterConfig(max_shortlist_candidates=10),
        gemini=GeminiConfig(top_k_recommendations=3, prompt_version="vtest"),
    )


def _fake_llm(system: str, user: str) -> str:
    return json.dumps(
        {
            "summary": "Mock summary for API test",
            "recommendations": [
                {"restaurant_id": "api-t2", "rank": 1, "explanation": "Great value South Indian."},
                {"restaurant_id": "api-t1", "rank": 2, "explanation": "Upscale Italian option."},
            ],
        }
    )


def test_recommend_missing_location_returns_422() -> None:
    app = create_app(catalog_df=_tiny_catalog(), cfg=_cfg(), generate_fn=_fake_llm)
    with TestClient(app) as client:
        r = client.post("/api/v1/recommend", json={"min_rating": 0})
    assert r.status_code == 422


def test_recommend_no_matches_returns_200_empty_items() -> None:
    app = create_app(catalog_df=_tiny_catalog(), cfg=_cfg(), generate_fn=_fake_llm)
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/recommend",
            json={"location": "NonexistentPlace", "min_rating": 0},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert "No restaurants matched" in data["summary"] or "location" in data["summary"].lower()
    assert data["meta"]["used_llm"] is False
    assert data["meta"]["filter_empty_reason"] == "NO_LOCATION"


def test_recommend_success_with_mock_llm() -> None:
    app = create_app(catalog_df=_tiny_catalog(), cfg=_cfg(), generate_fn=_fake_llm)
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/recommend",
            json={"location": "ApiTestVille", "min_rating": 0.0},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["summary"] == "Mock summary for API test"
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "api-t2"
    assert data["items"][0]["rank"] == 1
    assert "South Indian" in data["items"][0]["explanation"]
    assert data["meta"]["used_llm"] is True
    assert data["meta"]["parse_fallback"] is False
    assert data["meta"]["shortlist_size"] == 2


def test_root_serves_web_index() -> None:
    app = create_app(catalog_df=_tiny_catalog(), cfg=_cfg(), serve_web_ui=True)
    with TestClient(app) as client:
        r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in (r.headers.get("content-type") or "")
    assert b"Restaurant recommendations" in r.content


def test_static_css_served() -> None:
    app = create_app(catalog_df=_tiny_catalog(), cfg=_cfg(), serve_web_ui=True)
    with TestClient(app) as client:
        r = client.get("/static/styles.css")
    assert r.status_code == 200
    assert "text/css" in (r.headers.get("content-type") or "") or len(r.content) > 50
