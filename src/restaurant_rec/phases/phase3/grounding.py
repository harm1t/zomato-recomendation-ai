"""Keep LLM output aligned with catalog ids (architecture: no hallucinated venues)."""

from __future__ import annotations

from typing import List, Set

import pandas as pd

from restaurant_rec.phases.phase3.models import LlmRecommendationItem, LlmRecommendationPayload


def valid_ids_from_shortlist(shortlist: pd.DataFrame) -> Set[str]:
    return {str(x) for x in shortlist["id"].astype(str)}


def grounded_recommendations(
    payload: LlmRecommendationPayload,
    valid_ids: Set[str],
    top_k: int,
) -> List[LlmRecommendationItem]:
    """Preserve model order by ``rank``, drop unknown ids and duplicates."""
    ordered = sorted(payload.recommendations, key=lambda r: (r.rank, r.restaurant_id))
    seen: Set[str] = set()
    out: List[LlmRecommendationItem] = []
    for item in ordered:
        rid = str(item.restaurant_id).strip()
        if rid in valid_ids and rid not in seen:
            seen.add(rid)
            out.append(
                LlmRecommendationItem(
                    restaurant_id=rid,
                    rank=len(out) + 1,
                    explanation=item.explanation.strip(),
                )
            )
        if len(out) >= top_k:
            break
    return out


def heuristic_from_shortlist(shortlist: pd.DataFrame, top_k: int) -> LlmRecommendationPayload:
    """Fallback when JSON parsing fails (architecture §3.5)."""
    rows: List[LlmRecommendationItem] = []
    for i, (_, r) in enumerate(shortlist.head(top_k).iterrows(), start=1):
        rows.append(
            LlmRecommendationItem(
                restaurant_id=str(r["id"]),
                rank=i,
                explanation="Ranked from the catalog shortlist (AI response unavailable).",
            )
        )
    return LlmRecommendationPayload(
        summary="Showing top matches from the filtered catalog.",
        recommendations=rows,
    )
