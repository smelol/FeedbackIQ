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


if __name__ == "__main__":
    show_tables()