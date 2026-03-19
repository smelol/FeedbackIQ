import json
from datetime import datetime, timedelta, UTC

from src.db import get_connection
from src.reports.metrics import (
    get_total_reviews,
    get_total_analyzed,
    get_sentiment_distribution,
    get_top_categories,
)


def seed_review(location_id: int, rating: int, created_at: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO unified_reviews (
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
        "api",
        f"review-{location_id}-{rating}-{created_at}",
        location_id,
        rating,
        "comentario",
        None,
        created_at,
        created_at,
    ))

    review_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return review_id


def seed_analysis(review_id: int, sentiment: str, categories: list[str], analyzed_at: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO review_analysis (
            unified_review_id,
            sentiment,
            categories,
            summary,
            urgency,
            analyzed_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        review_id,
        sentiment,
        json.dumps(categories),
        "resumen",
        2,
        analyzed_at,
    ))

    conn.commit()
    conn.close()


def test_report_metrics_basic_counts(test_db):
    now = datetime.now(UTC).isoformat()
    since_iso = (datetime.now(UTC) - timedelta(days=7)).isoformat()

    r1 = seed_review(1, 5, now)
    r2 = seed_review(2, 1, now)

    seed_analysis(r1, "positive", ["servicio"], now)
    seed_analysis(r2, "negative", ["limpieza"], now)

    assert get_total_reviews(since_iso) == 2
    assert get_total_analyzed(since_iso) == 2


def test_sentiment_distribution(test_db):
    now = datetime.now(UTC).isoformat()
    since_iso = (datetime.now(UTC) - timedelta(days=7)).isoformat()

    r1 = seed_review(1, 5, now)
    r2 = seed_review(2, 1, now)
    r3 = seed_review(3, 3, now)

    seed_analysis(r1, "positive", ["servicio"], now)
    seed_analysis(r2, "negative", ["limpieza"], now)
    seed_analysis(r3, "negative", ["otro"], now)

    distribution = get_sentiment_distribution(since_iso)

    totals = {item["sentiment"]: item["total"] for item in distribution}
    assert totals["negative"] == 2
    assert totals["positive"] == 1


def test_top_categories(test_db):
    now = datetime.now(UTC).isoformat()
    since_iso = (datetime.now(UTC) - timedelta(days=7)).isoformat()

    r1 = seed_review(1, 5, now)
    r2 = seed_review(2, 1, now)

    seed_analysis(r1, "positive", ["servicio", "ambiente"], now)
    seed_analysis(r2, "negative", ["servicio"], now)

    categories = get_top_categories(since_iso)
    totals = {item["category"]: item["total"] for item in categories}

    assert totals["servicio"] == 2
    assert totals["ambiente"] == 1