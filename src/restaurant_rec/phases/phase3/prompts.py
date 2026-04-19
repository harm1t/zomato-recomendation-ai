"""System and user prompts for Gemini (architecture §3.2, §3.4)."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from restaurant_rec.phases.phase2.preferences import UserPreferences


def build_system_instruction(top_k: int) -> str:
    return (
        "You are an expert dining assistant for restaurants in India. "
        "You MUST only recommend restaurants whose `restaurant_id` appears in the "
        "provided JSON list. Do not invent venues, ratings, or prices. "
        f"Return at most {top_k} recommendations, ordered by `rank` starting at 1. "
        "Each explanation must be at most one short paragraph and must cite concrete "
        "facts from the data (cuisine, rating, cost, area). "
        "If the candidate list is empty, return {\"summary\": \"...\", \"recommendations\": []}. "
        "Reply with JSON only matching the schema: "
        '{"summary": string, "recommendations": '
        '[{"restaurant_id": string, "rank": int, "explanation": string}]}.'
    )


def _prefs_summary(prefs: UserPreferences) -> str:
    parts = [
        f"location: {prefs.location}",
        f"min_rating: {prefs.min_rating}",
    ]
    if prefs.budget_min_inr is not None and prefs.budget_max_inr is not None:
        parts.append(f"budget range (cost for two, INR): {prefs.budget_min_inr} to {prefs.budget_max_inr}")
    elif prefs.budget_min_inr is not None:
        parts.append(f"min budget (cost for two, INR): {prefs.budget_min_inr}")
    elif prefs.budget_max_inr is not None:
        parts.append(f"max budget (cost for two, INR): {prefs.budget_max_inr}")
    if prefs.has_cuisine_filter():
        parts.append(f"cuisine preference: {', '.join(prefs.cuisine_queries())}")
    if prefs.extras:
        parts.append(f"additional notes: {prefs.extras.strip()}")
    return "; ".join(parts)


def shortlist_rows_for_prompt(rows: List[Dict[str, Any]]) -> str:
    return json.dumps(rows, ensure_ascii=False, indent=2)


def build_user_message(prefs: UserPreferences, restaurant_rows: List[Dict[str, Any]]) -> str:
    return (
        "User preferences:\n"
        f"{_prefs_summary(prefs)}\n\n"
        "Candidate restaurants (JSON array). Use only these `restaurant_id` values:\n"
        f"{shortlist_rows_for_prompt(restaurant_rows)}"
    )


def json_only_retry_suffix() -> str:
    return (
        "\n\nYour previous reply was not valid JSON. "
        "Respond with ONLY a single JSON object, no markdown fences, matching the schema."
    )
