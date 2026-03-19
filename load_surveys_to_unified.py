from datetime import datetime, timedelta, UTC

from src.db import get_connection
from src.etl import transform_survey_to_unified, insert_unified_review


def load_surveys():
    conn = get_connection()
    cursor = conn.cursor()

    since = datetime.now(UTC) - timedelta(days=7)
    since_iso = since.isoformat()

    cursor.execute("""
        SELECT *
        FROM customer_surveys
        WHERE created_at >= ?
        ORDER BY created_at DESC
    """, (since_iso,))

    surveys = cursor.fetchall()
    conn.close()

    inserted_count = 0
    duplicate_count = 0

    for survey in surveys:
        unified_review = transform_survey_to_unified(survey)
        inserted = insert_unified_review(**unified_review)

        if inserted == 1:
            inserted_count += 1
        else:
            duplicate_count += 1

    result = {
        "processed": len(surveys),
        "inserted": inserted_count,
        "duplicates": duplicate_count,
    }

    print("Encuestas procesadas:", result["processed"])
    print("Reviews nuevas insertadas:", result["inserted"])
    print("Duplicadas ignoradas:", result["duplicates"])

    return result


if __name__ == "__main__":
    load_surveys()