"""HTTP request/response models (architecture §4.2)."""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from restaurant_rec.phases.phase2.preferences import UserPreferences
from restaurant_rec.phases.phase3.orchestration import RecommendationMeta, RecommendationResult


class RecommendRequest(BaseModel):
    """JSON body for ``POST /api/v1/recommend`` (maps to Phase 2 preferences)."""

    location: str = Field(..., min_length=1)
    budget_min_inr: Optional[int] = Field(default=None, ge=0)
    budget_max_inr: Optional[int] = Field(default=None, ge=0)
    cuisine: Optional[Union[str, List[str]]] = None
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    extras: Optional[str] = None

    def to_user_preferences(self) -> UserPreferences:
        return UserPreferences(
            location=self.location,
            budget_min_inr=self.budget_min_inr,
            budget_max_inr=self.budget_max_inr,
            cuisine=self.cuisine,
            min_rating=self.min_rating,
            extras=self.extras,
        )


class RecommendationItemOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    cuisines: List[str]
    rating: Optional[float] = None
    estimated_cost: str = ""
    cost_display: str = ""
    explanation: str = ""
    rank: int


class RecommendMetaOut(BaseModel):
    shortlist_size: int
    model: str
    prompt_version: str
    used_llm: bool = False
    parse_fallback: bool = False
    filter_empty_reason: Optional[str] = None
    rating_relaxed: bool = False
    min_rating_effective: float = 0.0
    after_location: int = 0
    after_cuisine: int = 0
    after_rating: int = 0
    after_budget: int = 0


class RecommendResponse(BaseModel):
    summary: str
    items: List[RecommendationItemOut]
    meta: RecommendMetaOut

    @classmethod
    def from_result(cls, result: RecommendationResult) -> RecommendResponse:
        m: RecommendationMeta = result.meta
        meta = RecommendMetaOut(
            shortlist_size=m.shortlist_size,
            model=m.model,
            prompt_version=m.prompt_version,
            used_llm=m.used_llm,
            parse_fallback=m.parse_fallback,
            filter_empty_reason=m.filter_empty_reason,
            rating_relaxed=m.rating_relaxed,
            min_rating_effective=m.min_rating_effective,
            after_location=m.after_location,
            after_cuisine=m.after_cuisine,
            after_rating=m.after_rating,
            after_budget=m.after_budget,
        )
        items = [RecommendationItemOut.model_validate(x) for x in result.items]
        return cls(summary=result.summary, items=items, meta=meta)
