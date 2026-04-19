"""Gemini API client via ``google-genai`` (architecture §3.1, §3.6)."""

from __future__ import annotations

import os
from typing import Optional

from restaurant_rec.core.config import AppConfig
from restaurant_rec.phases.phase3.env_load import load_dotenv_from_repo


def get_gemini_api_key() -> str:
    """Read ``GOOGLE_API_KEY`` or ``GEMINI_API_KEY`` after loading ``.env``."""
    load_dotenv_from_repo()
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key or not str(key).strip():
        raise RuntimeError(
            "Missing Gemini API key: set GOOGLE_API_KEY or GEMINI_API_KEY in .env or the environment."
        )
    return str(key).strip()


def generate_recommendation_text(
    *,
    system_instruction: str,
    user_message: str,
    cfg: AppConfig,
    api_key: Optional[str] = None,
) -> str:
    """
    Call ``generate_content`` with JSON-oriented config.

    ``api_key`` may be injected for tests; otherwise loaded via ``get_gemini_api_key()``.
    """
    from google import genai
    from google.genai import types

    key = api_key if api_key is not None else get_gemini_api_key()
    client = genai.Client(api_key=key)
    g = cfg.gemini
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=g.temperature,
        max_output_tokens=g.max_output_tokens,
        response_mime_type="application/json",
    )
    resp = client.models.generate_content(
        model=g.model,
        contents=user_message,
        config=config,
    )
    text = getattr(resp, "text", None) or ""
    return str(text).strip()
