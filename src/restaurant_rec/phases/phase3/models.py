"""Pydantic models for Gemini JSON output (architecture §3.3)."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class LlmRecommendationItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    restaurant_id: str
    rank: int
    explanation: str = ""


class LlmRecommendationPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    summary: str = ""
    recommendations: List[LlmRecommendationItem] = Field(default_factory=list)
