from __future__ import annotations

import pandas as pd

from restaurant_rec.phases.phase3.grounding import (
    grounded_recommendations,
    heuristic_from_shortlist,
    valid_ids_from_shortlist,
)
from restaurant_rec.phases.phase3.models import LlmRecommendationItem, LlmRecommendationPayload


def test_valid_ids() -> None:
    df = pd.DataFrame([{"id": "x"}, {"id": "y"}])
    assert valid_ids_from_shortlist(df) == {"x", "y"}


def test_grounding_drops_unknown_and_redundant_rank() -> None:
    payload = LlmRecommendationPayload(
        summary="s",
        recommendations=[
            LlmRecommendationItem(restaurant_id="bad", rank=1, explanation="a"),
            LlmRecommendationItem(restaurant_id="ok", rank=2, explanation="b"),
            LlmRecommendationItem(restaurant_id="ok", rank=3, explanation="c"),
        ],
    )
    out = grounded_recommendations(payload, {"ok"}, top_k=5)
    assert len(out) == 1
    assert out[0].restaurant_id == "ok"
    assert out[0].rank == 1


def test_heuristic_shortlist() -> None:
    df = pd.DataFrame(
        [
            {"id": "a", "name": "A", "cuisines": ["X"], "rating": 4.0, "votes": 1},
            {"id": "b", "name": "B", "cuisines": ["Y"], "rating": 3.0, "votes": 2},
        ]
    )
    h = heuristic_from_shortlist(df, top_k=1)
    assert len(h.recommendations) == 1
    assert h.recommendations[0].restaurant_id == "a"
