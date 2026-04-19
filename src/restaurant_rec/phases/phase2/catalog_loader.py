"""Load processed Phase 1 Parquet into a pandas DataFrame."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from restaurant_rec.core.config import AppConfig, load_config, repo_root


def load_catalog(
    path: Optional[Path] = None,
    *,
    config_path: Optional[Path] = None,
    project_root: Optional[Path] = None,
    cfg: Optional[AppConfig] = None,
) -> pd.DataFrame:
    """
    Read ``restaurants.parquet`` from config or an explicit path.

    ``project_root`` is used to resolve relative paths in config (repo root).
    """
    app_cfg = cfg or load_config(config_path)
    root = project_root or repo_root()
    catalog_path = path if path is not None else app_cfg.resolved_processed_catalog(project_root=root)
    if not catalog_path.is_file():
        raise FileNotFoundError(f"Catalog not found: {catalog_path}")
    return pd.read_parquet(catalog_path)
