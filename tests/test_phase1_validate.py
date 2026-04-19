from __future__ import annotations

from restaurant_rec.core.config import AppConfig, BudgetTiersConfig, RatingConfig
from restaurant_rec.phases.phase1.transform import hf_row_to_canonical
from restaurant_rec.phases.phase1.validate import validation_reason


def _cfg() -> AppConfig:
    return AppConfig(
        budget_tiers=BudgetTiersConfig(low_max_inr=400, medium_max_inr=800),
        rating=RatingConfig(),
    )


def test_drop_missing_name() -> None:
    row = hf_row_to_canonical(
        {
            "name": "  ",
            "location": "X",
            "listed_in(city)": "Y",
            "cuisines": "",
            "rate": "",
            "votes": 0,
            "approx_cost(for two people)": "",
            "address": "",
            "url": "",
        },
        _cfg(),
    )
    assert validation_reason(row) == "MISSING_NAME"


def test_drop_missing_location() -> None:
    row = hf_row_to_canonical(
        {
            "name": "Foo",
            "location": "",
            "listed_in(city)": "",
            "cuisines": "Italian",
            "rate": "4/5",
            "votes": 1,
            "approx_cost(for two people)": "500",
            "address": "",
            "url": "u",
        },
        _cfg(),
    )
    assert validation_reason(row) == "MISSING_LOCATION"


def test_keep_valid_row() -> None:
    row = hf_row_to_canonical(
        {
            "name": "Foo",
            "location": "Indiranagar",
            "listed_in(city)": "Bangalore",
            "cuisines": "Italian",
            "rate": "4/5",
            "votes": 1,
            "approx_cost(for two people)": "500",
            "address": "",
            "url": "https://example.com/r/1",
        },
        _cfg(),
    )
    assert validation_reason(row) is None
