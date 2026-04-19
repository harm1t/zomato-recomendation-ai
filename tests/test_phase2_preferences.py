from __future__ import annotations

import pytest
from pydantic import ValidationError

from restaurant_rec.phases.phase2.preferences import UserPreferences


def test_user_preferences_cuisine_list() -> None:
    p = UserPreferences(location="Indiranagar", cuisine=["Chinese", "Thai"])
    assert p.cuisine_queries() == ["chinese", "thai"]


def test_user_preferences_cuisine_string_split() -> None:
    p = UserPreferences(location="X", cuisine="North Indian, Chinese")
    assert p.cuisine_queries() == ["north indian", "chinese"]


def test_user_preferences_no_cuisine_filter() -> None:
    p = UserPreferences(location="X", cuisine=None)
    assert not p.has_cuisine_filter()


def test_location_trimmed() -> None:
    p = UserPreferences(location="  Bangalore  ")
    assert p.location == "Bangalore"


def test_location_whitespace_rejected() -> None:
    with pytest.raises(ValidationError):
        UserPreferences(location="   ")
