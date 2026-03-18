from src.db import get_connection
from src.etl import transform_survey_to_unified, insert_unified_review


def load_surveys():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customer_surveys
        ORDER BY created_at DESC
    """)

    surveys = cursor.fetchall()
    conn.close()

    inserted_count = 0

    for survey in surveys:
        unified_review = transform_survey_to_unified(survey)
        inserted = insert_unified_review(**unified_review)
        inserted_count += inserted

    print(f"Encuestas procesadas: {len(surveys)}")
    print(f"Reviews nuevas insertadas: {inserted_count}")


if __name__ == "__main__":
    load_surveys()