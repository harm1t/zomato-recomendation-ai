from __future__ import annotations

import pytest

import restaurant_rec.phases.phase3.gemini_client as gc


def test_get_gemini_api_key_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gc, "load_dotenv_from_repo", lambda: None)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="Missing Gemini API key"):
        gc.get_gemini_api_key()


def test_get_gemini_api_key_from_google(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gc, "load_dotenv_from_repo", lambda: None)
    monkeypatch.setenv("GOOGLE_API_KEY", " test-key ")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert gc.get_gemini_api_key() == "test-key"
