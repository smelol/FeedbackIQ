from datetime import datetime, UTC
from src.db import get_connection


def insert_alert(severity: str, location_id: int, rule_code: str, message: str, dedupe_key: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO alerts (
            severity,
            location_id,
            rule_code,
            message,
            dedupe_key,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        severity,
        location_id,
        rule_code,
        message,
        dedupe_key,
        datetime.now(UTC).isoformat(),
    ))

    conn.commit()
    inserted = cursor.rowcount
    conn.close()

    return inserted