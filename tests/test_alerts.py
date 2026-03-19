import json
from datetime import datetime, timedelta, UTC

from src.db import get_connection
from src.alerts.rules import (
    detect_critical_reviews,
    detect_negative_spike_24h,
    detect_low_weekly_average,
)
from src.alerts.repository import insert_alert


def insert_review_with_analysis(
    location_id: int,
    rating: int,
    created_at: str,
    sentiment: str,
    urgency: int,
    text: str = "comentario",
):
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
        f"seed-{location_id}-{rating}-{created_at}",
        location_id,
        rating,
        text,
        None,
        created_at,
        created_at,
    ))

    review_id = cursor.lastrowid

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
        json.dumps(["otro"]),
        "resumen",
        urgency,
        created_at,
    ))

    conn.commit()
    conn.close()

    return review_id


def test_detect_critical_reviews(test_db):
    now = datetime.now(UTC).isoformat()

    review_id = insert_review_with_analysis(
        location_id=3,
        rating=1,
        created_at=now,
        sentiment="negative",
        urgency=5,
        text="Encontré vidrio en mi bebida",
    )

    alerts = detect_critical_reviews()

    assert len(alerts) == 1
    assert alerts[0]["severity"] == "CRITICA"
    assert alerts[0]["location_id"] == 3
    assert alerts[0]["dedupe_key"] == f"critical_review_{review_id}"


def test_detect_negative_spike_24h(test_db):
    now = datetime.now(UTC)

    for _ in range(3):
        insert_review_with_analysis(
            location_id=2,
            rating=1,
            created_at=(now - timedelta(hours=2)).isoformat(),
            sentiment="negative",
            urgency=2,
            text="Muy mala experiencia",
        )

    alerts = detect_negative_spike_24h()

    assert len(alerts) == 1
    assert alerts[0]["severity"] == "ALTA"
    assert alerts[0]["location_id"] == 2
    assert alerts[0]["rule_code"] == "NEGATIVE_SPIKE_24H"


def test_detect_low_weekly_average(test_db):
    now = datetime.now(UTC)

    ratings = [1, 2, 2, 3]
    for rating in ratings:
        insert_review_with_analysis(
            location_id=11,
            rating=rating,
            created_at=(now - timedelta(days=2)).isoformat(),
            sentiment="negative",
            urgency=2,
            text="Mal servicio",
        )

    alerts = detect_low_weekly_average()

    assert len(alerts) == 1
    assert alerts[0]["severity"] == "MEDIA"
    assert alerts[0]["location_id"] == 11
    assert alerts[0]["rule_code"] == "LOW_WEEKLY_AVERAGE"


def test_insert_alert_is_deduplicated(test_db):
    first = insert_alert(
        severity="ALTA",
        location_id=2,
        rule_code="NEGATIVE_SPIKE_24H",
        message="Local 2 con muchas negativas",
        dedupe_key="negative_spike_2_2026-03-18",
    )

    second = insert_alert(
        severity="ALTA",
        location_id=2,
        rule_code="NEGATIVE_SPIKE_24H",
        message="Local 2 con muchas negativas",
        dedupe_key="negative_spike_2_2026-03-18",
    )

    assert first == 1
    assert second == 0