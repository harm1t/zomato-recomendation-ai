"""Phase 2: user preferences, catalog load, deterministic filtering."""

from restaurant_rec.phases.phase2.catalog_loader import load_catalog
from restaurant_rec.phases.phase2.filter import (
    FilterResult,
    distinct_cities,
    distinct_localities,
    filter_restaurants,
)
from restaurant_rec.phases.phase2.preferences import UserPreferences

__all__ = [
    "FilterResult",
    "UserPreferences",
    "distinct_cities",
    "distinct_localities",
    "filter_restaurants",
    "load_catalog",
]
