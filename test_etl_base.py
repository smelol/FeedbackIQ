from datetime import datetime, UTC, timedelta
from src.etl import insert_unified_review
from src.db import get_connection


def seed_unified_reviews():
    now = datetime.now(UTC)

    sample_reviews = [
        {
            "source": "api",
            "source_review_id": "r1001",
            "location_id": 1,
            "rating": 5,
            "text": "Los nachos estaban muy ricos",
            "author": "Laura",
            "created_at": (now - timedelta(hours=3)).isoformat(),
        },
        {
            "source": "api",
            "source_review_id": "r1002",
            "location_id": 2,
            "rating": 1,
            "text": "Las empanadas muy grasosas",
            "author": "Luis",
            "created_at": (now - timedelta(hours=2)).isoformat(),
        },
        {
            "source": "survey",
            "source_review_id": "1",
            "location_id": 1,
            "rating": 2,
            "text": "La comida llegó fría",
            "author": "ana@example.com",
            "created_at": (now - timedelta(days=1)).isoformat(),
        },
    ]

    inserted_count = 0

    for review in sample_reviews:
        inserted = insert_unified_review(**review)
        inserted_count += inserted

    print(f"Reviews insertadas: {inserted_count}")


def show_unified_reviews():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM unified_reviews
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    print("\nUnified reviews:")
    for row in rows:
        print(dict(row))

    conn.close()


if __name__ == "__main__":
    seed_unified_reviews()
    show_unified_reviews()