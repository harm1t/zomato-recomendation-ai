"""Canonical catalog row (post Phase 1)."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


BudgetTier = Literal["low", "medium", "high"]


class CatalogRestaurant(BaseModel):
    """Single restaurant record stored in ``restaurants.parquet``."""

    id: str
    name: str
    locality: str = ""
    city: str = ""
    cuisines: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    cost_for_two: Optional[int] = None
    budget_tier: Optional[BudgetTier] = None
    votes: int = 0
    address: str = ""
    url: str = ""
    raw_features: str = ""
