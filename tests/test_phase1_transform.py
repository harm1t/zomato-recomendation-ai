"""Unit tests for HF → canonical transforms."""

from __future__ import annotations

from restaurant_rec.core.config import AppConfig, BudgetTiersConfig, RatingConfig
from restaurant_rec.phases.phase1.transform import (
    HF_COST_COL,
    apply_city_alias,
    budget_tier_for_cost,
    hf_row_to_canonical,
    parse_cost_inr,
    parse_cuisines,
    parse_rating,
    stable_restaurant_id,
)


def _cfg() -> AppConfig:
    return AppConfig(
        budget_tiers=BudgetTiersConfig(low_max_inr=400, medium_max_inr=800),
        city_aliases={"Bengaluru": "Bangalore"},
        rating=RatingConfig(min_valid=0.0, max_valid=5.0),
    )


def test_parse_rating_slash_format() -> None:
    assert parse_rating("4.1/5", 0, 5) == 4.1
    assert parse_rating("  3 / 5 ", 0, 5) == 3.0


def test_parse_rating_plain_number() -> None:
    assert parse_rating("4.5", 0, 5) == 4.5


def test_parse_rating_invalid() -> None:
    assert parse_rating("NEW", 0, 5) is None
    assert parse_rating("", 0, 5) is None
    assert parse_rating("9/5", 0, 5) is None


def test_parse_cost_inr() -> None:
    assert parse_cost_inr("800") == 800
    assert parse_cost_inr("1,200") == 1200
    assert parse_cost_inr("") is None


def test_parse_cuisines() -> None:
    assert parse_cuisines("North Indian, Chinese") == ["North Indian", "Chinese"]
    assert parse_cuisines("A | B") == ["A", "B"]


def test_budget_tier() -> None:
    cfg = _cfg()
    assert budget_tier_for_cost(300, cfg) == "low"
    assert budget_tier_for_cost(500, cfg) == "medium"
    assert budget_tier_for_cost(900, cfg) == "high"
    assert budget_tier_for_cost(None, cfg) is None


def test_city_alias() -> None:
    assert apply_city_alias("Bengaluru", {"Bengaluru": "Bangalore"}) == "Bangalore"


def test_hf_row_to_canonical_sample() -> None:
    cfg = _cfg()
    row = {
        "name": "Jalsa",
        "location": "Banashankari",
        "listed_in(city)": "Banashankari",
        "cuisines": "North Indian, Mughlai, Chinese",
        "rate": "4.1/5",
        "votes": 775,
        HF_COST_COL: "800",
        "address": "942 Main Rd",
        "url": "https://zomato.com/x",
        "rest_type": "Casual Dining",
        "dish_liked": "Biryani",
        "online_order": "Yes",
        "book_table": "No",
        "listed_in(type)": "Buffet",
    }
    out = hf_row_to_canonical(row, cfg)
    assert out["name"] == "Jalsa"
    assert out["locality"] == "Banashankari"
    assert out["city"] == "Banashankari"
    assert out["cuisines"] == ["North Indian", "Mughlai", "Chinese"]
    assert out["rating"] == 4.1
    assert out["cost_for_two"] == 800
    assert out["budget_tier"] == "medium"
    assert out["votes"] == 775
    assert out["id"] == stable_restaurant_id("Jalsa", "Banashankari", "Banashankari", "https://zomato.com/x")
    assert "rest_type" in out["raw_features"]
