from src.db import get_connection


def show_counts():
    conn = get_connection()
    cursor = conn.cursor()

    tables = [
        "customer_surveys",
        "unified_reviews",
        "review_analysis",
        "alerts",
    ]

    print("Conteos generales:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) AS total FROM {table}")
        row = cursor.fetchone()
        print(f"- {table}: {row['total']}")

    conn.close()


if __name__ == "__main__":
    show_counts()