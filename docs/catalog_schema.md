# Catalog schema (Phase 1)

Processed artifact: `data/processed/restaurants.parquet` (see `config.yaml` → `paths.processed_catalog`).

Reproduce:

```bash
cd /path/to/project
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python scripts/ingest_zomato.py
```

## Fields

| Column | Type | Source (Hugging Face) | Notes |
|--------|------|------------------------|--------|
| `id` | string | derived | SHA-256 of normalized `name`, `locality`, `city`, `url`. |
| `name` | string | `name` | Required. |
| `locality` | string | `location` | Area / neighborhood. |
| `city` | string | `listed_in(city)` | Normalized with `city_aliases` in `config.yaml`. |
| `cuisines` | list\<string\> | `cuisines` | Split on comma or pipe. |
| `rating` | float or null | `rate` | Parsed from values like `4.1/5`; invalid → null. |
| `cost_for_two` | int or null | `approx_cost(for two people)` | Digits only (INR). |
| `budget_tier` | string or null | derived | `low` / `medium` / `high` from `budget_tiers` in config; null if cost unknown. |
| `votes` | int | `votes` | Tie-break for shortlist (Phase 2). |
| `address` | string | `address` | |
| `url` | string | `url` | Stabilizes `id`. |
| `raw_features` | string | derived | JSON with `rest_type`, `dish_liked`, `online_order`, `book_table`, `listed_in_type` when present. |

## Example row (JSON)

```json
{
  "id": "a1b2c3d4e5f6…",
  "name": "Jalsa",
  "locality": "Banashankari",
  "city": "Banashankari",
  "cuisines": ["North Indian", "Mughlai", "Chinese"],
  "rating": 4.1,
  "cost_for_two": 800,
  "budget_tier": "medium",
  "votes": 775,
  "address": "942, 21st Main Road, 2nd Stage, Banashankari, Bangalore",
  "url": "https://www.zomato.com/bangalore/jalsa-banashankari?context=…",
  "raw_features": "{\"rest_type\": \"Casual Dining\", \"dish_liked\": \"Pasta, Lunch Buffet…\", \"online_order\": \"Yes\", \"book_table\": \"Yes\", \"listed_in_type\": \"Buffet\"}"
}
```

## Row drops

| Reason | Meaning |
|--------|---------|
| `MISSING_NAME` | Empty `name` after trim. |
| `MISSING_LOCATION` | Both `locality` and `city` empty. |
| `INVALID_MODEL` | Failed `CatalogRestaurant` validation. |

Duplicate `id` values are merged to one row (higher `votes`, then higher `rating`). The ingest summary prints `duplicates_merged=N`.
