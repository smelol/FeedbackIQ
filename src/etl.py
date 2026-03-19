from datetime import datetime, UTC
from src.db import get_connection


def insert_unified_review(
    source,
    source_review_id,
    location_id,
    rating,
    text,
    author,
    created_at,
):
    conn = get_connection()
    cursor = conn.cursor()

    ingested_at = datetime.now(UTC).isoformat()

    cursor.execute("""
        INSERT OR IGNORE INTO unified_reviews (
            source,
            source_review_id,
            location_id,
            rating,
            text,
            author,
            created_at,
            ingested_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        source,
        str(source_review_id),
        location_id,
        rating,
        text,
        author,
        created_at,
        ingested_at,
    ))

    conn.commit()
    inserted = cursor.rowcount
    conn.close()

    return inserted

def transform_survey_to_unified(survey_row):
    return {
        "source": "survey",
        "source_review_id": str(survey_row["id"]),
        "location_id": survey_row["location_id"],
        "rating": survey_row["rating"],
        "text": clean_text(survey_row["comments"]),
        "author": clean_text(survey_row["customer_email"]),
        "created_at": survey_row["created_at"],
    }

def transform_api_review_to_unified(api_review):
    return {
        "source": "api",
        "source_review_id": str(api_review["review_id"]),
        "location_id": api_review["location_id"],
        "rating": api_review["rating"],
        "text": clean_text(api_review["text"]),
        "author": clean_text(api_review["author"]),
        "created_at": api_review["created_at"],
    }

def clean_text(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value