"""Validated user preferences for catalog filtering."""

from __future__ import annotations

import re
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class UserPreferences(BaseModel):
    """
    Structured preferences aligned with the problem statement and architecture.

    ``location`` matches catalog ``locality`` or ``city`` (case-insensitive, trimmed).
    """

    location: str = Field(..., min_length=1, description="Locality or city from catalog")
    budget_min_inr: Optional[int] = Field(
        default=None,
        ge=0,
        description="Keep rows with known cost_for_two >= this value; None skips min budget filter",
    )
    budget_max_inr: Optional[int] = Field(
        default=None,
        ge=0,
        description="Keep rows with known cost_for_two <= this value; None skips max budget filter",
    )
    cuisine: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="Substring match against cuisine list; None or empty = any cuisine",
    )
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    extras: Optional[str] = Field(
        default=None,
        description="Free text for LLM (Phase 3); optional tie-break keyword overlap in Phase 2",
    )

    @field_validator("location")
    @classmethod
    def strip_location(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("location cannot be empty or whitespace")
        return s

    @field_validator("cuisine", mode="before")
    @classmethod
    def coerce_cuisine(cls, v: Optional[Union[str, List[str]]]) -> Optional[Union[str, List[str]]]:
        if v is None:
            return None
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        s = str(v).strip()
        return s if s else None

    def cuisine_queries(self) -> List[str]:
        """Normalized non-empty cuisine tokens for matching."""
        c = self.cuisine
        if c is None:
            return []
        if isinstance(c, str):
            parts = re.split(r"[,|]", c)
            return [p.strip().lower() for p in parts if p.strip()]
        return [str(x).strip().lower() for x in c if str(x).strip()]

    def has_cuisine_filter(self) -> bool:
        return bool(self.cuisine_queries())
