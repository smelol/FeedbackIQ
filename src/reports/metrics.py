import json
from datetime import datetime, timedelta, UTC

from src.db import get_connection


def get_since_iso(days: int = 7) -> str:
    return (datetime.now(UTC) - timedelta(days=days)).isoformat()


def get_total_reviews(since_iso: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM unified_reviews
        WHERE created_at >= ?
    """, (since_iso,))

    total = cursor.fetchone()["total"]
    conn.close()
    return total


def get_total_analyzed(since_iso: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM review_analysis ra
        JOIN unified_reviews ur ON ur.id = ra.unified_review_id
        WHERE ur.created_at >= ?
    """, (since_iso,))

    total = cursor.fetchone()["total"]
    conn.close()
    return total


def get_total_alerts(since_iso: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM alerts
        WHERE created_at >= ?
    """, (since_iso,))

    total = cursor.fetchone()["total"]
    conn.close()
    return total


def get_sentiment_distribution(since_iso: str) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ra.sentiment, COUNT(*) AS total
        FROM review_analysis ra
        JOIN unified_reviews ur ON ur.id = ra.unified_review_id
        WHERE ur.created_at >= ?
        GROUP BY ra.sentiment
        ORDER BY total DESC
    """, (since_iso,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_top_rated_locations(since_iso: str, limit: int = 3) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            location_id,
            ROUND(AVG(rating), 2) AS avg_rating,
            COUNT(*) AS total_reviews
        FROM unified_reviews
        WHERE created_at >= ?
        GROUP BY location_id
        HAVING COUNT(*) >= 3
        ORDER BY avg_rating DESC, total_reviews DESC
        LIMIT ?
    """, (since_iso, limit))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_problematic_locations(since_iso: str, limit: int = 3) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ur.location_id,
            COUNT(*) AS negative_reviews,
            ROUND(AVG(ur.rating), 2) AS avg_rating
        FROM review_analysis ra
        JOIN unified_reviews ur ON ur.id = ra.unified_review_id
        WHERE ur.created_at >= ?
          AND ra.sentiment = 'negative'
        GROUP BY ur.location_id
        HAVING COUNT(*) >= 1
        ORDER BY negative_reviews DESC, avg_rating ASC
        LIMIT ?
    """, (since_iso, limit))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_top_categories(since_iso: str, limit: int = 5) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ra.categories
        FROM review_analysis ra
        JOIN unified_reviews ur ON ur.id = ra.unified_review_id
        WHERE ur.created_at >= ?
    """, (since_iso,))

    counts = {}

    for row in cursor.fetchall():
        categories = json.loads(row["categories"])
        for category in categories:
            counts[category] = counts.get(category, 0) + 1

    conn.close()

    items = [
        {"category": category, "total": total}
        for category, total in counts.items()
    ]

    items.sort(key=lambda x: x["total"], reverse=True)
    return items[:limit]


def get_recent_alerts(limit: int = 10) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT severity, location_id, rule_code, message, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def build_report_metrics() -> dict:
    since_iso = get_since_iso(7)

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "total_reviews": get_total_reviews(since_iso),
        "total_analyzed": get_total_analyzed(since_iso),
        "total_alerts": get_total_alerts(since_iso),
        "sentiment_distribution": get_sentiment_distribution(since_iso),
        "top_rated_locations": get_top_rated_locations(since_iso),
        "problematic_locations": get_problematic_locations(since_iso),
        "top_categories": get_top_categories(since_iso),
        "recent_alerts": get_recent_alerts(),
    }