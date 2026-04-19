"""Load shared configuration from config.yaml at the project root."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


def repo_root() -> Path:
    """Repository root (contains ``config.yaml``, ``data/``, ``scripts/``)."""
    cwd = Path.cwd()
    if (cwd / "config.yaml").exists() and (cwd / "data").exists():
        return cwd
    # src/restaurant_rec/core/config.py -> parents[3] == repo root
    return Path(__file__).resolve().parents[3]


def _default_config_path() -> Path:
    return repo_root() / "config.yaml"


class PathsConfig(BaseModel):
    processed_catalog: str = "data/processed/restaurants.parquet"


class DatasetConfig(BaseModel):
    hf_name: str = "ManikaSaini/zomato-restaurant-recommendation"
    split: str = "train"


class BudgetTiersConfig(BaseModel):
    low_max_inr: int = 400
    medium_max_inr: int = 800


class RatingConfig(BaseModel):
    min_valid: float = 0.0
    max_valid: float = 5.0


class FilterConfig(BaseModel):
    """Phase 2 shortlist cap and optional min_rating relax (architecture §2.3)."""

    max_shortlist_candidates: int = 40
    relax_min_rating: bool = False
    min_rating_relax_delta: float = 0.5


class GeminiConfig(BaseModel):
    """Phase 3 Gemini settings (API key from ``.env`` — see architecture §3.6)."""

    model: str = "gemini-2.0-flash"
    temperature: float = 0.3
    max_output_tokens: int = 2048
    top_k_recommendations: int = 5
    prompt_version: str = "v1"


class AppConfig(BaseModel):
    paths: PathsConfig = Field(default_factory=PathsConfig)
    dataset: DatasetConfig = Field(default_factory=DatasetConfig)
    budget_tiers: BudgetTiersConfig = Field(default_factory=BudgetTiersConfig)
    city_aliases: dict[str, str] = Field(default_factory=dict)
    rating: RatingConfig = Field(default_factory=RatingConfig)
    filter: FilterConfig = Field(default_factory=FilterConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)

    def resolved_processed_catalog(self, project_root: Path | None = None) -> Path:
        root = project_root or repo_root()
        return (root / self.paths.processed_catalog).resolve()


def load_config(path: Path | str | None = None) -> AppConfig:
    cfg_path = Path(path) if path else _default_config_path()
    data: dict[str, Any] = {}
    if cfg_path.is_file():
        with cfg_path.open(encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        if isinstance(raw, dict):
            data = raw
    return AppConfig.model_validate(data)
