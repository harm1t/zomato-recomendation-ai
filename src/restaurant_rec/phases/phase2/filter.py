"""Deterministic shortlist from catalog + preferences."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pandas as pd

from restaurant_rec.core.config import AppConfig, FilterConfig, load_config
from restaurant_rec.phases.phase1.transform import apply_city_alias
from restaurant_rec.phases.phase2.preferences import UserPreferences


def _norm_loc(s: str) -> str:
    return s.strip().lower()


def _row_cuisines_list(val) -> List[str]:
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return []
    if isinstance(val, list):
        return [str(x) for x in val]
    s = str(val).strip()
    if not s:
        return []
    parts = re.split(r"[,|]", s)
    return [p.strip() for p in parts if p.strip()]


def _location_mask(df: pd.DataFrame, user_location: str, city_aliases: dict) -> pd.Series:
    loc_user = _norm_loc(apply_city_alias(user_location.strip(), city_aliases))
    loc_col = df["locality"].fillna("").map(_norm_loc)
    city_col = df["city"].fillna("").map(_norm_loc)
    return (loc_col == loc_user) | (city_col == loc_user)


def _cuisine_mask(df: pd.DataFrame, queries: List[str]) -> pd.Series:
    if not queries:
        return pd.Series(True, index=df.index)

    def row_matches(cval) -> bool:
        cuisines = _row_cuisines_list(cval)
        hay = " ".join(c.lower() for c in cuisines)
        return any(q in hay for q in queries)

    return df["cuisines"].map(row_matches)


def _rating_mask(df: pd.Series, min_rating: float) -> pd.Series:
    r = pd.to_numeric(df, errors="coerce")
    return r.notna() & (r >= min_rating)


def _budget_mask(cost: pd.Series, budget_min: Optional[int], budget_max: Optional[int]) -> pd.Series:
    if budget_min is None and budget_max is None:
        return pd.Series(True, index=cost.index)
    c = pd.to_numeric(cost, errors="coerce")
    m = c.notna()
    if budget_min is not None:
        m &= (c >= budget_min)
    if budget_max is not None:
        m &= (c <= budget_max)
    return m


def _extras_tie_score_row(
    name: str,
    cuisines_val,
    raw_features: str,
    extras: Optional[str],
) -> int:
    if not extras or not str(extras).strip():
        return 0
    tokens = [t for t in re.findall(r"[a-z0-9]+", str(extras).lower()) if len(t) > 2]
    if not tokens:
        return 0
    cu = _row_cuisines_list(cuisines_val)
    hay = " ".join(
        [
            str(name).lower(),
            " ".join(x.lower() for x in cu),
            str(raw_features or "").lower(),
        ]
    )
    return sum(1 for t in tokens if t in hay)


@dataclass
class FilterStageCounts:
    after_location: int
    after_cuisine: int
    after_rating: int
    after_budget: int


@dataclass
class FilterResult:
    """Shortlist DataFrame plus diagnostics for API / UI."""

    shortlist: pd.DataFrame
    counts: FilterStageCounts
    empty_reason: Optional[str]
    rating_relaxed: bool
    min_rating_effective: float


def _first_empty_reason(counts: FilterStageCounts) -> Optional[str]:
    if counts.after_location == 0:
        return "NO_LOCATION"
    if counts.after_cuisine == 0:
        return "NO_CUISINE"
    if counts.after_rating == 0:
        return "NO_RATING"
    if counts.after_budget == 0:
        return "NO_BUDGET"
    return None


def filter_restaurants(
    catalog_df: pd.DataFrame,
    prefs: UserPreferences,
    *,
    cfg: Optional[AppConfig] = None,
    max_candidates: Optional[int] = None,
) -> FilterResult:
    """
    Apply location → cuisine → rating → budget, then sort and cap shortlist.

    Location matches ``locality`` or ``city`` (case-insensitive). User location
    is normalized with ``city_aliases`` from config when applicable.
    """
    app_cfg = cfg or load_config()
    fcfg: FilterConfig = app_cfg.filter
    cap = max_candidates if max_candidates is not None else fcfg.max_shortlist_candidates

    df = catalog_df.copy()
    required = {"locality", "city", "cuisines", "rating", "votes"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"catalog_df missing columns: {sorted(missing)}")

    m_loc = _location_mask(df, prefs.location, app_cfg.city_aliases)
    d1 = df.loc[m_loc]
    c1 = int(len(d1))

    cuisine_queries = prefs.cuisine_queries()
    if prefs.has_cuisine_filter():
        m_c = _cuisine_mask(d1, cuisine_queries)
        d2 = d1.loc[m_c]
    else:
        d2 = d1
    c2 = int(len(d2))

    rating_relaxed = False
    min_eff = float(prefs.min_rating)
    m_r = _rating_mask(d2["rating"], min_eff)
    d3 = d2.loc[m_r]
    c3 = int(len(d3))

    if c3 == 0 and fcfg.relax_min_rating and c2 > 0:
        new_min = max(0.0, min_eff - fcfg.min_rating_relax_delta)
        if new_min < min_eff:
            m_r2 = _rating_mask(d2["rating"], new_min)
            d3 = d2.loc[m_r2]
            c3 = int(len(d3))
            if c3 > 0:
                rating_relaxed = True
                min_eff = new_min

    m_b = _budget_mask(d3["cost_for_two"], prefs.budget_min_inr, prefs.budget_max_inr)
    d4 = d3.loc[m_b]
    c4 = int(len(d4))

    counts = FilterStageCounts(
        after_location=c1,
        after_cuisine=c2,
        after_rating=c3,
        after_budget=c4,
    )
    reason = _first_empty_reason(counts)

    if c4 == 0:
        empty = pd.DataFrame(columns=df.columns)
        return FilterResult(
            shortlist=empty,
            counts=counts,
            empty_reason=reason,
            rating_relaxed=rating_relaxed,
            min_rating_effective=min_eff,
        )

    scored = d4.copy()
    scored["_extras_score"] = scored.apply(
        lambda r: _extras_tie_score_row(
            str(r.get("name", "")),
            r.get("cuisines"),
            str(r.get("raw_features", "") or ""),
            prefs.extras,
        ),
        axis=1,
    )
    scored["_rating_sort"] = pd.to_numeric(scored["rating"], errors="coerce").fillna(-1.0)
    scored = scored.sort_values(
        by=["_rating_sort", "votes", "_extras_score"],
        ascending=[False, False, False],
        kind="mergesort",
    )
    capped = scored.head(cap).drop(columns=["_extras_score", "_rating_sort"], errors="ignore")

    return FilterResult(
        shortlist=capped.reset_index(drop=True),
        counts=counts,
        empty_reason=None,
        rating_relaxed=rating_relaxed,
        min_rating_effective=min_eff,
    )


def distinct_localities(catalog_df: pd.DataFrame, *, limit: Optional[int] = None) -> List[str]:
    """Sorted unique locality strings (non-empty)."""
    s = catalog_df["locality"].dropna().astype(str).str.strip()
    s = s[s != ""]
    out = sorted(s.unique(), key=str.casefold)
    if limit is not None:
        return out[:limit]
    return out


def distinct_cities(catalog_df: pd.DataFrame, *, limit: Optional[int] = None) -> List[str]:
    """Sorted unique city strings (non-empty)."""
    s = catalog_df["city"].dropna().astype(str).str.strip()
    s = s[s != ""]
    out = sorted(s.unique(), key=str.casefold)
    if limit is not None:
        return out[:limit]
    return out
