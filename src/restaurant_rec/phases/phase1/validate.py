"""Row-level validation and drop reasons for catalog build."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from restaurant_rec.phases.phase1.schema import CatalogRestaurant


def validation_reason(row: dict[str, Any]) -> str | None:
    """
    Return a drop reason code, or None if the row should be kept.

    Rows without a usable name or without any location anchor (locality and city)
    are dropped; invalid Pydantic payloads are dropped as ``INVALID_MODEL``.
    """
    name = (row.get("name") or "").strip()
    if not name:
        return "MISSING_NAME"

    locality = (row.get("locality") or "").strip()
    city = (row.get("city") or "").strip()
    if not locality and not city:
        return "MISSING_LOCATION"

    try:
        CatalogRestaurant.model_validate(row)
    except ValidationError:
        return "INVALID_MODEL"
    return None
