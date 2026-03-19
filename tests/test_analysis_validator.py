import pytest

from src.analysis.validator import validate_analysis


def test_validate_analysis_accepts_valid_payload(test_db):
    payload = {
        "sentiment": "negative",
        "categories": ["servicio", "limpieza"],
        "summary": "Servicio lento y lugar sucio",
        "urgency": 4,
    }

    result = validate_analysis(payload)

    assert result["sentiment"] == "negative"
    assert result["categories"] == ["servicio", "limpieza"]
    assert result["summary"] == "Servicio lento y lugar sucio"
    assert result["urgency"] == 4


def test_validate_analysis_filters_invalid_categories(test_db):
    payload = {
        "sentiment": "negative",
        "categories": ["inventada", "servicio"],
        "summary": "Mala atención",
        "urgency": 2,
    }

    result = validate_analysis(payload)

    assert result["categories"] == ["servicio"]


def test_validate_analysis_falls_back_to_otro(test_db):
    payload = {
        "sentiment": "neutral",
        "categories": ["inventada"],
        "summary": "Regular",
        "urgency": 1,
    }

    result = validate_analysis(payload)

    assert result["categories"] == ["otro"]


def test_validate_analysis_rejects_invalid_sentiment(test_db):
    payload = {
        "sentiment": "bad",
        "categories": ["otro"],
        "summary": "Texto",
        "urgency": 1,
    }

    with pytest.raises(ValueError):
        validate_analysis(payload)


def test_validate_analysis_rejects_invalid_urgency(test_db):
    payload = {
        "sentiment": "positive",
        "categories": ["otro"],
        "summary": "Texto",
        "urgency": 9,
    }

    with pytest.raises(ValueError):
        validate_analysis(payload)


def test_validate_analysis_truncates_long_summary(test_db):
    payload = {
        "sentiment": "positive",
        "categories": ["otro"],
        "summary": "x" * 140,
        "urgency": 1,
    }

    result = validate_analysis(payload)

    assert len(result["summary"]) == 100