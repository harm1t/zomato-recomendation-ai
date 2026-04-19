"""Load ``.env`` from the repository root (Phase 3 / Gemini API key)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from restaurant_rec.core.config import repo_root


def load_dotenv_from_repo(path: Optional[Path] = None) -> None:
    """Load ``.env`` into ``os.environ`` if ``python-dotenv`` is installed."""
    try:
        from dotenv import load_dotenv as _load
    except ImportError:
        return
    root = path or repo_root()
    env_file = root / ".env"
    if env_file.is_file():
        _load(env_file)
