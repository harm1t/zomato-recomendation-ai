"""Map Hugging Face Zomato rows to the canonical catalog schema."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from restaurant_rec.core.config import AppConfig
from restaurant_rec.phases.phase1.schema import BudgetTier

# HF dataset column for approximate cost (literal key from Hugging Face)
HF_COST_COL = "approx_cost(for two people)"


def _norm_str(v: Any) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return s


def apply_city_alias(city: str, aliases: dict[str, str]) -> str:
    if not city:
        return city
    if city in aliases:
        return aliases[city]
    lower = city.lower()
    for k, v in aliases.items():
        if k.lower() == lower:
            return v
    return city


def parse_rating(rate_raw: Any, rmin: float, rmax: float) -> float | None:
    s = _norm_str(rate_raw)
    if not s or s.upper() in {"NEW", "-", "NAN"}:
        return None
    m = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*/\s*5\s*$", s, re.I)
    if m:
        val = float(m.group(1))
        if rmin <= val <= rmax:
            return val
        return None
    m2 = re.match(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*$", s)
    if m2:
        val = float(m2.group(1))
        if rmin <= val <= rmax:
            return val
    return None


def parse_cost_inr(cost_raw: Any) -> int | None:
    s = _norm_str(cost_raw)
    if not s or s in {"-", "nan"}:
        return None
    digits = re.sub(r"[^\d]", "", s)
    if not digits:
        return None
    return int(digits)


def parse_cuisines(cuisines_raw: Any) -> list[str]:
    s = _norm_str(cuisines_raw)
    if not s:
        return []
    parts = re.split(r"[,|]", s)
    return [p.strip() for p in parts if p.strip()]


def budget_tier_for_cost(cost: int | None, cfg: AppConfig) -> BudgetTier | None:
    if cost is None:
        return None
    low_m = cfg.budget_tiers.low_max_inr
    med_m = cfg.budget_tiers.medium_max_inr
    if cost <= low_m:
        return "low"
    if cost <= med_m:
        return "medium"
    return "high"


def stable_restaurant_id(name: str, locality: str, city: str, url: str) -> str:
    key = "|".join(
        [
            _norm_str(name).lower(),
            _norm_str(locality).lower(),
            _norm_str(city).lower(),
            _norm_str(url),
        ]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def build_raw_features(row: dict[str, Any]) -> str:
    """Compact JSON blob for optional LLM / filter hints (Phase 2+)."""
    bits = {
        "rest_type": _norm_str(row.get("rest_type")),
        "dish_liked": _norm_str(row.get("dish_liked"))[:500],
        "online_order": _norm_str(row.get("online_order")),
        "book_table": _norm_str(row.get("book_table")),
        "listed_in_type": _norm_str(row.get("listed_in(type)")),
    }
    bits = {k: v for k, v in bits.items() if v}
    if not bits:
        return ""
    return json.dumps(bits, ensure_ascii=False)


def hf_row_to_canonical(row: dict[str, Any], cfg: AppConfig) -> dict[str, Any]:
    name = _norm_str(row.get("name"))
    locality = _norm_str(row.get("location"))
    city_raw = _norm_str(row.get("listed_in(city)"))
    city = apply_city_alias(city_raw, cfg.city_aliases)
    url = _norm_str(row.get("url"))
    cost = parse_cost_inr(row.get(HF_COST_COL))
    rating = parse_rating(row.get("rate"), cfg.rating.min_valid, cfg.rating.max_valid)
    cuisines = parse_cuisines(row.get("cuisines"))
    rid = stable_restaurant_id(name, locality, city, url)
    tier = budget_tier_for_cost(cost, cfg)
    votes = row.get("votes")
    try:
        votes_int = int(votes) if votes is not None and str(votes).strip() != "" else 0
    except (TypeError, ValueError):
        votes_int = 0

    return {
        "id": rid,
        "name": name,
        "locality": locality,
        "city": city,
        "cuisines": cuisines,
        "rating": rating,
        "cost_for_two": cost,
        "budget_tier": tier,
        "votes": votes_int,
        "address": _norm_str(row.get("address")),
        "url": url,
        "raw_features": build_raw_features(row),
    }
