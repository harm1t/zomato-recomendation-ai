from __future__ import annotations

from restaurant_rec.phases.phase3.parse import parse_llm_json


def test_parse_plain_json() -> None:
    text = '{"summary": "Hi", "recommendations": [{"restaurant_id": "a", "rank": 1, "explanation": "x"}]}'
    p = parse_llm_json(text)
    assert p is not None
    assert p.summary == "Hi"
    assert len(p.recommendations) == 1
    assert p.recommendations[0].restaurant_id == "a"


def test_parse_json_fenced() -> None:
    text = '```json\n{"summary": "", "recommendations": []}\n```'
    p = parse_llm_json(text)
    assert p is not None
    assert p.recommendations == []


def test_parse_invalid() -> None:
    assert parse_llm_json("not json") is None
    assert parse_llm_json("") is None
