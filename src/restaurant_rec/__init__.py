"""Restaurant recommendation package (phased pipeline: catalog → filter → LLM → API)."""

from restaurant_rec.core.config import AppConfig, load_config, repo_root

__all__ = ["AppConfig", "load_config", "repo_root"]
