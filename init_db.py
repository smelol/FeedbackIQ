from src.db import get_connection


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_surveys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        comments TEXT,
        customer_email TEXT,
        created_at TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS unified_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL CHECK (source IN ('api', 'survey')),
        source_review_id TEXT NOT NULL,
        location_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
        text TEXT,
        author TEXT,
        created_at TEXT NOT NULL,
        ingested_at TEXT NOT NULL,
        UNIQUE(source, source_review_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS review_analysis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unified_review_id INTEGER NOT NULL,
        sentiment TEXT NOT NULL CHECK (sentiment IN ('positive', 'negative', 'neutral')),
        categories TEXT NOT NULL,
        summary TEXT NOT NULL,
        urgency INTEGER NOT NULL CHECK (urgency >= 1 AND urgency <= 5),
        analyzed_at TEXT NOT NULL,
        FOREIGN KEY (unified_review_id) REFERENCES unified_reviews(id) ON DELETE CASCADE,
        UNIQUE(unified_review_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        severity TEXT NOT NULL CHECK (severity IN ('MEDIA', 'ALTA', 'CRITICA')),
        location_id INTEGER NOT NULL,
        rule_code TEXT NOT NULL,
        message TEXT NOT NULL,
        dedupe_key TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente.")