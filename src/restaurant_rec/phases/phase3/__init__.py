"""Phase 3: Gemini prompts, JSON parse, grounding, ``recommend()`` orchestration."""

from restaurant_rec.phases.phase3.gemini_client import generate_recommendation_text, get_gemini_api_key
from restaurant_rec.phases.phase3.models import LlmRecommendationItem, LlmRecommendationPayload
from restaurant_rec.phases.phase3.orchestration import (
    RecommendationMeta,
    RecommendationResult,
    recommend,
    shortlist_to_llm_rows,
)

__all__ = [
    "LlmRecommendationItem",
    "LlmRecommendationPayload",
    "RecommendationMeta",
    "RecommendationResult",
    "generate_recommendation_text",
    "get_gemini_api_key",
    "recommend",
    "shortlist_to_llm_rows",
]
