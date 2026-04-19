"""Phase 3 orchestration: filter → Gemini → parse → grounded items (architecture §3.5)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import pandas as pd

from restaurant_rec.core.config import AppConfig, load_config
from restaurant_rec.phases.phase2.filter import filter_restaurants
from restaurant_rec.phases.phase2.preferences import UserPreferences
from restaurant_rec.phases.phase3.gemini_client import generate_recommendation_text
from restaurant_rec.phases.phase3.grounding import (
    grounded_recommendations,
    heuristic_from_shortlist,
    valid_ids_from_shortlist,
)
from restaurant_rec.phases.phase3.models import LlmRecommendationPayload
from restaurant_rec.phases.phase3.parse import parse_llm_json
from restaurant_rec.phases.phase3.prompts import (
    build_system_instruction,
    build_user_message,
    json_only_retry_suffix,
)

FILTER_EMPTY_SUMMARY = {
    "NO_LOCATION": "No restaurants matched that location. Try another area from the catalog.",
    "NO_CUISINE": "No restaurants matched that cuisine in this area. Try a broader cuisine or location.",
    "NO_RATING": "No restaurants met the minimum rating with the current filters.",
    "NO_BUDGET": "No restaurants matched your budget. Try a higher budget or remove the cap.",
}


def shortlist_to_llm_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Compact rows for the user prompt (architecture §3.2)."""
    rows: List[Dict[str, Any]] = []
    for _, r in df.iterrows():
        cuisines = r["cuisines"]
        if isinstance(cuisines, (list, tuple)):
            cu: Any = [str(x) for x in cuisines]
        else:
            cu = str(cuisines) if cuisines is not None and str(cuisines).strip() else []
        cost = r.get("cost_for_two")
        cost_v = None
        if cost is not None and not (isinstance(cost, float) and np.isnan(cost)):
            try:
                cost_v = int(cost)
            except (TypeError, ValueError):
                cost_v = None
        rt = r.get("rating")
        rating_v = None
        if rt is not None and not (isinstance(rt, float) and np.isnan(rt)):
            try:
                rating_v = float(rt)
            except (TypeError, ValueError):
                rating_v = None
        rows.append(
            {
                "restaurant_id": str(r["id"]),
                "name": str(r.get("name", "")),
                "cuisines": cu,
                "rating": rating_v,
                "cost_for_two_inr": cost_v,
                "locality": str(r.get("locality", "") or ""),
                "city": str(r.get("city", "") or ""),
            }
        )
    return rows


def _cost_display(row: pd.Series) -> str:
    c = row.get("cost_for_two")
    if c is None or (isinstance(c, float) and np.isnan(c)):
        return ""
    try:
        return f"₹{int(c)} for two"
    except (TypeError, ValueError):
        return ""


def _estimated_cost(row: pd.Series) -> str:
    bt = row.get("budget_tier")
    if bt is not None and str(bt).strip():
        if isinstance(bt, float) and np.isnan(bt):
            pass
        else:
            return str(bt)
    c = row.get("cost_for_two")
    if c is not None and not (isinstance(c, float) and np.isnan(c)):
        try:
            return f"₹{int(c)}"
        except (TypeError, ValueError):
            pass
    return ""


def _cuisines_for_display(row: pd.Series) -> List[str]:
    v = row.get("cuisines")
    if isinstance(v, list):
        return [str(x) for x in v]
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return []
    s = str(v).strip()
    if not s:
        return []
    return [p.strip() for p in re.split(r"[,|]", s) if p.strip()]


def _lookup_row(shortlist: pd.DataFrame, rid: str) -> Optional[pd.Series]:
    m = shortlist[shortlist["id"].astype(str) == str(rid)]
    if m.empty:
        return None
    return m.iloc[0]


def _build_display_items(
    shortlist: pd.DataFrame,
    payload: LlmRecommendationPayload,
    top_k: int,
) -> List[Dict[str, Any]]:
    vids = valid_ids_from_shortlist(shortlist)
    grounded = grounded_recommendations(payload, vids, top_k)
    items: List[Dict[str, Any]] = []
    for rec in grounded:
        row = _lookup_row(shortlist, rec.restaurant_id)
        if row is None:
            continue
        rt = row.get("rating")
        rating_out = float(rt) if rt is not None and not (isinstance(rt, float) and np.isnan(rt)) else None
        items.append(
            {
                "id": str(row["id"]),
                "name": str(row.get("name", "")),
                "cuisines": _cuisines_for_display(row),
                "rating": rating_out,
                "estimated_cost": _estimated_cost(row),
                "cost_display": _cost_display(row),
                "explanation": rec.explanation,
                "rank": rec.rank,
            }
        )
    return items


@dataclass
class RecommendationMeta:
    shortlist_size: int
    model: str
    prompt_version: str
    filter_empty_reason: Optional[str] = None
    used_llm: bool = False
    parse_fallback: bool = False
    rating_relaxed: bool = False
    min_rating_effective: float = 0.0
    after_location: int = 0
    after_cuisine: int = 0
    after_rating: int = 0
    after_budget: int = 0


@dataclass
class RecommendationResult:
    """API-shaped result (aligns with architecture Phase 4 §4.2)."""

    summary: str
    items: List[Dict[str, Any]]
    meta: RecommendationMeta


GenerateFn = Callable[[str, str], str]


def recommend(
    catalog_df: pd.DataFrame,
    prefs: UserPreferences,
    *,
    cfg: Optional[AppConfig] = None,
    api_key: Optional[str] = None,
    generate_fn: Optional[GenerateFn] = None,
) -> RecommendationResult:
    """
    Run Phase 2 filter, then Gemini ranking/explanations, then merge with catalog rows.

    ``generate_fn(system, user) -> text`` overrides the real API (for unit tests).
    """
    app_cfg = cfg or load_config()
    top_k = app_cfg.gemini.top_k_recommendations
    fr = filter_restaurants(catalog_df, prefs, cfg=app_cfg)

    base_meta = RecommendationMeta(
        shortlist_size=0,
        model=app_cfg.gemini.model,
        prompt_version=app_cfg.gemini.prompt_version,
        filter_empty_reason=fr.empty_reason,
        used_llm=False,
        parse_fallback=False,
        rating_relaxed=fr.rating_relaxed,
        min_rating_effective=fr.min_rating_effective,
        after_location=fr.counts.after_location,
        after_cuisine=fr.counts.after_cuisine,
        after_rating=fr.counts.after_rating,
        after_budget=fr.counts.after_budget,
    )

    if fr.empty_reason is not None or fr.shortlist.empty:
        summary = FILTER_EMPTY_SUMMARY.get(
            fr.empty_reason or "",
            "No restaurants matched your filters.",
        )
        return RecommendationResult(summary=summary, items=[], meta=base_meta)

    shortlist = fr.shortlist
    base_meta.shortlist_size = len(shortlist)
    llm_rows = shortlist_to_llm_rows(shortlist)
    system = build_system_instruction(top_k)
    user = build_user_message(prefs, llm_rows)

    def _call_llm(u: str) -> Optional[str]:
        if generate_fn is not None:
            return generate_fn(system, u)
        try:
            return generate_recommendation_text(
                system_instruction=system,
                user_message=u,
                cfg=app_cfg,
                api_key=api_key,
            )
        except Exception as e:
            print(f"Warning: LLM generation failed: {e}")
            return None

    parse_fallback = False
    text = _call_llm(user)
    payload = None
    
    if text is not None:
        payload = parse_llm_json(text)
        if payload is None and generate_fn is None:
            text2 = _call_llm(user + json_only_retry_suffix())
            if text2 is not None:
                payload = parse_llm_json(text2)

    if payload is None:
        payload = heuristic_from_shortlist(shortlist, top_k)
        parse_fallback = True

    items = _build_display_items(shortlist, payload, top_k)
    summary = payload.summary.strip() or "Here are tailored picks based on your preferences."

    meta = RecommendationMeta(
        shortlist_size=len(shortlist),
        model=app_cfg.gemini.model,
        prompt_version=app_cfg.gemini.prompt_version,
        filter_empty_reason=None,
        used_llm=True,
        parse_fallback=parse_fallback,
        rating_relaxed=fr.rating_relaxed,
        min_rating_effective=fr.min_rating_effective,
        after_location=fr.counts.after_location,
        after_cuisine=fr.counts.after_cuisine,
        after_rating=fr.counts.after_rating,
        after_budget=fr.counts.after_budget,
    )

    return RecommendationResult(summary=summary, items=items, meta=meta)
