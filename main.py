from src.db import get_connection


def show_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name;
    """)

    tables = cursor.fetchall()

    print("Tablas en la base de datos:")
    for table in tables:
        print("-", table["name"])

    conn.close()

def show_analysis():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ur.text, ra.sentiment, ra.summary, ra.urgency
        FROM review_analysis ra
        JOIN unified_reviews ur
        ON ur.id = ra.unified_review_id
        LIMIT 10
    """)

    for row in cursor.fetchall():
        print(dict(row))

    conn.close()

def show_alerts():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT severity, location_id, rule_code, message, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    print("Alertas:")
    for row in rows:
        print(dict(row))

    conn.close()


if __name__ == "__main__":
    # show_tables()
    # show_analysis()
    show_alerts()