from datetime import datetime, UTC
import json

from src.db import get_connection
from src.analysis.prompts import build_prompt
from src.analysis.llm_client import analyze_text
from src.analysis.validator import validate_analysis


def get_unanalyzed_reviews(limit=50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ur.*
        FROM unified_reviews ur
        LEFT JOIN review_analysis ra
        ON ur.id = ra.unified_review_id
        WHERE ra.id IS NULL
        ORDER BY ur.created_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows


def save_analysis(unified_review_id: int, result: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO review_analysis (
            unified_review_id,
            sentiment,
            categories,
            summary,
            urgency,
            analyzed_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        unified_review_id,
        result["sentiment"],
        json.dumps(result["categories"]),
        result["summary"],
        result["urgency"],
        datetime.now(UTC).isoformat(),
    ))

    conn.commit()
    conn.close()


def run_analysis(batch_size=50):
    reviews = get_unanalyzed_reviews(limit=batch_size)

    print(f"Reviews a analizar: {len(reviews)}")

    success = 0
    failed = 0

    for review in reviews:
        try:
            prompt = build_prompt(
                text=(review["text"] or "").strip() or "Sin comentario",
                rating=review["rating"]
            )

            raw = analyze_text(prompt)
            validated = validate_analysis(raw)

            save_analysis(review["id"], validated)
            success += 1

        except Exception as e:
            print(f"[ERROR] review_id={review['id']}: {e}")
            failed += 1

    result = {
        "attempted": len(reviews),
        "success": success,
        "failed": failed,
    }

    print("\nResumen análisis:")
    print(f"✔ exitosos: {result['success']}")
    print(f"✖ fallidos: {result['failed']}")

    return result