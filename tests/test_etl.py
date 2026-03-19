from src.db import get_connection
from src.etl import (
    clean_text,
    insert_unified_review,
    transform_survey_to_unified,
    transform_api_review_to_unified,
)


def test_clean_text_handles_none_and_spaces():
    assert clean_text(None) is None
    assert clean_text("") is None
    assert clean_text("   ") is None
    assert clean_text(" hola ") == "hola"


def test_transform_survey_to_unified(test_db):
    survey_row = {
        "id": 123,
        "location_id": 4,
        "rating": 2,
        "comments": "  servicio malo  ",
        "customer_email": " test@example.com ",
        "created_at": "2026-03-18T10:00:00+00:00",
    }

    result = transform_survey_to_unified(survey_row)

    assert result["source"] == "survey"
    assert result["source_review_id"] == "123"
    assert result["location_id"] == 4
    assert result["rating"] == 2
    assert result["text"] == "servicio malo"
    assert result["author"] == "test@example.com"


def test_transform_api_review_to_unified(test_db):
    api_review = {
        "review_id": "api-1",
        "location_id": 2,
        "rating": 5,
        "text": " excelente ",
        "author": " Ana ",
        "created_at": "2026-03-18T10:00:00+00:00",
    }

    result = transform_api_review_to_unified(api_review)

    assert result["source"] == "api"
    assert result["source_review_id"] == "api-1"
    assert result["text"] == "excelente"
    assert result["author"] == "Ana"


def test_insert_unified_review_is_idempotent(test_db):
    payload = {
        "source": "api",
        "source_review_id": "dup-1",
        "location_id": 1,
        "rating": 4,
        "text": "Muy bien",
        "author": "Carlos",
        "created_at": "2026-03-18T10:00:00+00:00",
    }

    first = insert_unified_review(**payload)
    second = insert_unified_review(**payload)

    assert first == 1
    assert second == 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM unified_reviews")
    total = cursor.fetchone()["total"]
    conn.close()

    assert total == 1