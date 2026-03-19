import json
from datetime import datetime, timedelta, UTC
from src.db import get_connection


def detect_critical_reviews():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ur.id AS unified_review_id,
            ur.location_id,
            ur.text,
            ra.urgency
        FROM review_analysis ra
        JOIN unified_reviews ur
            ON ur.id = ra.unified_review_id
        WHERE ra.urgency = 5
    """)

    rows = cursor.fetchall()
    conn.close()

    alerts = []

    for row in rows:
        excerpt = (row["text"] or "").strip()[:120]

        alerts.append({
            "severity": "CRITICA",
            "location_id": row["location_id"],
            "rule_code": "CRITICAL_URGENCY",
            "message": f"Review crítica detectada en local {row['location_id']}: {excerpt}",
            "dedupe_key": f"critical_review_{row['unified_review_id']}",
        })

    return alerts


def detect_negative_spike_24h():
    conn = get_connection()
    cursor = conn.cursor()

    since = (datetime.now(UTC) - timedelta(hours=24)).isoformat()

    cursor.execute("""
        SELECT
            ur.location_id,
            COUNT(*) AS negative_count
        FROM review_analysis ra
        JOIN unified_reviews ur
            ON ur.id = ra.unified_review_id
        WHERE ra.sentiment = 'negative'
          AND ur.created_at >= ?
        GROUP BY ur.location_id
        HAVING COUNT(*) >= 3
    """, (since,))

    rows = cursor.fetchall()
    conn.close()

    alerts = []

    for row in rows:
        location_id = row["location_id"]
        negative_count = row["negative_count"]

        alerts.append({
            "severity": "ALTA",
            "location_id": location_id,
            "rule_code": "NEGATIVE_SPIKE_24H",
            "message": f"Local {location_id} tiene {negative_count} reseñas negativas en las últimas 24 horas.",
            "dedupe_key": f"negative_spike_{location_id}_{datetime.now(UTC).date().isoformat()}",
        })

    return alerts


def detect_low_weekly_average():
    conn = get_connection()
    cursor = conn.cursor()

    since = (datetime.now(UTC) - timedelta(days=7)).isoformat()

    cursor.execute("""
        SELECT
            location_id,
            COUNT(*) AS total_reviews,
            AVG(rating) AS avg_rating
        FROM unified_reviews
        WHERE created_at >= ?
        GROUP BY location_id
        HAVING AVG(rating) < 3.5
    """, (since,))

    rows = cursor.fetchall()
    conn.close()

    alerts = []

    for row in rows:
        location_id = row["location_id"]
        avg_rating = row["avg_rating"]
        total_reviews = row["total_reviews"]

        alerts.append({
            "severity": "MEDIA",
            "location_id": location_id,
            "rule_code": "LOW_WEEKLY_AVERAGE",
            "message": (
                f"Local {location_id} tiene promedio semanal bajo: "
                f"{avg_rating:.2f} en {total_reviews} reseñas."
            ),
            "dedupe_key": f"low_weekly_avg_{location_id}_{datetime.now(UTC).date().isoformat()}",
        })

    return alerts