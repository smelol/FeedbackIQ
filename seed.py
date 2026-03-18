from datetime import datetime, timedelta, UTC
from src.db import get_connection


def seed_customer_surveys():
    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.now(UTC)

    surveys = [
        (1, 5, "Los nachos estaban muy ricos", "laura@hotmail.com", (now - timedelta(days=1)).isoformat()),
        (1, 2, "Las empanadas muy grasosas", "luis@example.com", (now - timedelta(days=2)).isoformat()),
        (2, 1, "Se demoraron toda la vida en traerme la sopa", None, (now - timedelta(hours=12)).isoformat()),
        (3, 4, "Todo bien, aunque algo demorado", "maria@example.com", (now - timedelta(days=3)).isoformat()),
    ]

    cursor.executemany("""
        INSERT INTO customer_surveys (location_id, rating, comments, customer_email, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, surveys)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_customer_surveys()
    print("Datos de prueba insertados en customer_surveys.")