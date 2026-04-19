"""Extract and validate JSON from Gemini text (architecture §3.3, §3.5)."""

from __future__ import annotations

import json
import re
from typing import Any, Optional, Tuple

from restaurant_rec.phases.phase3.models import LlmRecommendationPayload


def _strip_fences(text: str) -> str:
    s = text.strip()
    m = re.match(r"^```(?:json)?\s*([\s\S]*?)\s*```$", s, re.I)
    if m:
        return m.group(1).strip()
    return s


def parse_llm_json(text: str) -> Optional[LlmRecommendationPayload]:
    """Parse model output into ``LlmRecommendationPayload`` or return None."""
    if not text or not str(text).strip():
        return None
    raw = _strip_fences(str(text).strip())
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    try:
        return LlmRecommendationPayload.model_validate(data)
    except Exception:
        return None


def parse_or_none_with_raw(text: str) -> Tuple[Optional[LlmRecommendationPayload], str]:
    """Return (payload, cleaned_text_used)."""
    cleaned = _strip_fences(str(text).strip()) if text else ""
    return parse_llm_json(cleaned), cleaned
