"""
Live Gemini checks (requires network + API key in repo-root ``.env``).

Run only this file when validating connectivity:
  pytest tests/test_gemini_live_connection.py -v
"""

from __future__ import annotations

import json
import os

import pytest

from restaurant_rec.core.config import load_config
from restaurant_rec.phases.phase3.env_load import load_dotenv_from_repo
from restaurant_rec.phases.phase3.gemini_client import generate_recommendation_text, get_gemini_api_key
from restaurant_rec.phases.phase2.preferences import UserPreferences
from restaurant_rec.phases.phase3.orchestration import recommend

load_dotenv_from_repo()

pytestmark = pytest.mark.skipif(
    not (os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()),
    reason="Set GOOGLE_API_KEY or GEMINI_API_KEY in .env to run live Gemini tests",
)


def test_api_key_loads_and_has_sensible_length() -> None:
    key = get_gemini_api_key()
    assert len(key) >= 20, "API key looks too short — check .env"


def test_gemini_sdk_minimal_completion() -> None:
    """Direct ``google-genai`` call (no Phase 3 wrapper)."""
    from google import genai

    cfg = load_config()
    client = genai.Client(api_key=get_gemini_api_key())
    resp = client.models.generate_content(
        model=cfg.gemini.model,
        contents='Reply with exactly one word: "CONNECTED" (no punctuation).',
    )
    text = (getattr(resp, "text", None) or "").upper()
    assert "CONNECTED" in text, f"Unexpected model reply: {resp.text!r}"


def test_generate_recommendation_text_returns_json_object() -> None:
    """Phase 3 client uses JSON mime type; response must parse as JSON."""
    cfg = load_config()
    text = generate_recommendation_text(
        system_instruction='Always respond with JSON only: {"status": "ok"}',
        user_message="ping",
        cfg=cfg,
    )
    data = json.loads(text)
    assert data.get("status") == "ok"


def test_recommend_pipeline_single_restaurant() -> None:
    """End-to-end: filter → Gemini → grounded item (tiny catalog)."""
    import pandas as pd

    cfg = load_config()
    df = pd.DataFrame(
        [
            {
                "id": "live-t1",
                "name": "Integration Test Diner",
                "locality": "LiveTestArea",
                "city": "LiveTestCity",
                "cuisines": ["Continental"],
                "rating": 4.2,
                "cost_for_two": 700,
                "votes": 42,
                "budget_tier": "medium",
                "address": "",
                "url": "https://example.com/live-t1",
                "raw_features": "{}",
            }
        ]
    )
    prefs = UserPreferences(location="LiveTestArea", min_rating=0.0)
    out = recommend(df, prefs, cfg=cfg)
    assert out.meta.used_llm is True
    assert out.meta.filter_empty_reason is None
    assert len(out.items) >= 1
    assert out.items[0]["id"] == "live-t1"
    assert out.items[0]["name"] == "Integration Test Diner"
    assert len(out.items[0].get("explanation", "")) > 0
