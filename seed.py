import json
import random
from datetime import datetime, timedelta, UTC
from pathlib import Path

from src.db import get_connection

API_SEED_PATH = Path("data/api_reviews_seed.json")

LOCATION_IDS = list(range(1, 16))

POSITIVE_TEXTS = [
    "Excelente atención y comida deliciosa",
    "Muy buena experiencia, volvería sin duda",
    "El servicio fue rápido y amable",
    "Todo estuvo muy rico",
    "Buen ambiente y personal atento",
    "La comida llegó a tiempo y en buen estado",
    "Muy satisfecho con la visita",
    "Todo salió perfecto",
]

NEUTRAL_TEXTS = [
    "Normal, nada especial",
    "Estuvo bien, pero puede mejorar",
    "La experiencia fue aceptable",
    "Todo más o menos bien",
    "Sin comentarios relevantes",
    "Regular, ni bueno ni malo",
]

NEGATIVE_TEXTS = [
    "La comida llegó fría",
    "Muy mala experiencia, el lugar estaba sucio",
    "Pésimo servicio, nadie resolvió nada",
    "Tardaron demasiado en atender",
    "La atención fue grosera",
    "No había varios productos del menú",
    "La orden llegó incompleta",
    "No volvería, muy decepcionante",
]

CRITICAL_TEXTS = [
    "Encontré un vidrio en mi bebida, esto es gravísimo",
    "Me sentí mal después de comer aquí, posible intoxicación",
    "Hubo trato agresivo por parte del personal",
    "La comida estaba en mal estado, esto es un riesgo sanitario",
]

FIRST_NAMES = [
    "Ana", "Luis", "Carlos", "Laura", "Pedro", "Sofía", "Marta",
    "Julián", "Valeria", "Daniel", "Camila", "Andrés", "Paula"
]

EMAIL_DOMAINS = ["mail.com", "example.com", "correo.com"]


def random_timestamp_within_last_days(days: int = 7) -> str:
    now = datetime.now(UTC)
    delta_seconds = random.randint(0, days * 24 * 60 * 60)
    dt = now - timedelta(seconds=delta_seconds)
    return dt.isoformat()


def random_email(name: str) -> str:
    slug = name.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    return f"{slug}{random.randint(1, 999)}@{random.choice(EMAIL_DOMAINS)}"


def choose_review_kind(location_id: int) -> str:
    """
    Hace algunos locales más problemáticos que otros.
    """
    roll = random.random()

    # Locales problemáticos para facilitar alertas
    if location_id in {2, 7, 11}:
        if roll < 0.10:
            return "critical"
        if roll < 0.55:
            return "negative"
        if roll < 0.75:
            return "neutral"
        return "positive"

    # Locales normales
    if roll < 0.03:
        return "critical"
    if roll < 0.23:
        return "negative"
    if roll < 0.45:
        return "neutral"
    return "positive"


def build_review_payload(location_id: int, source_prefix: str, index: int) -> dict:
    kind = choose_review_kind(location_id)

    if kind == "positive":
        rating = random.choice([4, 5])
        text = random.choice(POSITIVE_TEXTS)
    elif kind == "neutral":
        rating = random.choice([3, 4])
        text = random.choice(NEUTRAL_TEXTS)
    elif kind == "negative":
        rating = random.choice([1, 2])
        text = random.choice(NEGATIVE_TEXTS)
    else:
        rating = 1
        text = random.choice(CRITICAL_TEXTS)

    name = random.choice(FIRST_NAMES)

    if source_prefix == "api":
        author = None if random.random() < 0.25 else name
    else:
        author = None if random.random() < 0.20 else random_email(name)

    return {
        "source_review_id": f"{source_prefix}-{location_id}-{index}",
        "location_id": location_id,
        "rating": rating,
        "text": text,
        "author": author,
        "created_at": random_timestamp_within_last_days(7),
        "kind": kind,
    }


def reset_customer_surveys():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customer_surveys")
    conn.commit()
    conn.close()


def seed_customer_surveys(total_per_location: int = 30):
    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0

    for location_id in LOCATION_IDS:
        for index in range(total_per_location):
            payload = build_review_payload(location_id, "survey", index)

            comments = payload["text"]
            customer_email = payload["author"]

            # algunos comentarios vacíos / nulos
            if random.random() < 0.05:
                comments = None
            elif random.random() < 0.05:
                comments = "   "

            cursor.execute("""
                INSERT INTO customer_surveys (
                    location_id,
                    rating,
                    comments,
                    customer_email,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                payload["location_id"],
                payload["rating"],
                comments,
                customer_email,
                payload["created_at"],
            ))
            inserted += 1

    conn.commit()
    conn.close()
    return inserted


def build_api_reviews_seed(total_per_location: int = 35) -> list[dict]:
    reviews = []

    for location_id in LOCATION_IDS:
        for index in range(total_per_location):
            payload = build_review_payload(location_id, "api", index)

            reviews.append({
                "review_id": payload["source_review_id"],
                "location_id": payload["location_id"],
                "rating": payload["rating"],
                "text": payload["text"],
                "author": payload["author"],
                "created_at": payload["created_at"],
            })

    add_forced_alert_cases(reviews)
    add_api_duplicates(reviews, duplicate_ratio=0.08)

    random.shuffle(reviews)
    return reviews


def add_forced_alert_cases(reviews: list[dict]) -> None:
    """
    Casos dirigidos para garantizar alertas.
    """
    now = datetime.now(UTC)

    # Caso crítico claro
    reviews.append({
        "review_id": "api-critical-1",
        "location_id": 3,
        "rating": 1,
        "text": "Encontré un vidrio en mi bebida, esto es gravísimo",
        "author": "Pedro",
        "created_at": (now - timedelta(hours=2)).isoformat(),
    })

    # Pico de negativas en 24h para local 2
    reviews.extend([
        {
            "review_id": "api-spike-2-1",
            "location_id": 2,
            "rating": 1,
            "text": "Pésimo servicio, nadie resolvió nada",
            "author": "Ana",
            "created_at": (now - timedelta(hours=8)).isoformat(),
        },
        {
            "review_id": "api-spike-2-2",
            "location_id": 2,
            "rating": 1,
            "text": "La comida llegó fría y tardaron demasiado",
            "author": "Luis",
            "created_at": (now - timedelta(hours=7)).isoformat(),
        },
        {
            "review_id": "api-spike-2-3",
            "location_id": 2,
            "rating": 2,
            "text": "La atención fue grosera y el lugar estaba sucio",
            "author": "Marta",
            "created_at": (now - timedelta(hours=6)).isoformat(),
        },
    ])

    # Local 11 con promedio semanal malo
    for i in range(8):
        reviews.append({
            "review_id": f"api-lowavg-11-{i}",
            "location_id": 11,
            "rating": random.choice([1, 2, 2, 3]),
            "text": random.choice(NEGATIVE_TEXTS),
            "author": random.choice(FIRST_NAMES),
            "created_at": (now - timedelta(days=random.randint(1, 6))).isoformat(),
        })


def add_api_duplicates(reviews: list[dict], duplicate_ratio: float = 0.05) -> None:
    if not reviews:
        return

    original_count = len(reviews)
    duplicate_count = max(1, int(original_count * duplicate_ratio))

    chosen = random.sample(reviews, k=min(duplicate_count, len(reviews)))

    for item in chosen:
        reviews.append(item.copy())


def write_api_seed_file(reviews: list[dict]):
    API_SEED_PATH.parent.mkdir(parents=True, exist_ok=True)

    with API_SEED_PATH.open("w", encoding="utf-8") as f:
        json.dump(reviews, f, ensure_ascii=False, indent=2)

def summarize_api_reviews(reviews: list[dict]):
    by_location = {}
    by_rating = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    for review in reviews:
        loc = review["location_id"]
        by_location[loc] = by_location.get(loc, 0) + 1
        by_rating[review["rating"]] += 1

    print("\nResumen API:")
    print("Por rating:", by_rating)
    print("Locales con más reviews:")
    for loc, count in sorted(by_location.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  Local {loc}: {count}")

def summarize_surveys():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT location_id, COUNT(*) as total, AVG(rating) as avg_rating
        FROM customer_surveys
        GROUP BY location_id
        ORDER BY total DESC, location_id ASC
    """)

    rows = cursor.fetchall()

    print("\nResumen surveys:")
    for row in rows:
        print(
            f"Local {row['location_id']}: "
            f"total={row['total']}, avg_rating={row['avg_rating']:.2f}"
        )

    conn.close()


def main():
    random.seed(42)

    reset_customer_surveys()
    surveys_inserted = seed_customer_surveys(total_per_location=40)

    api_reviews = build_api_reviews_seed(total_per_location=45)
    write_api_seed_file(api_reviews)

    summarize_api_reviews(api_reviews)
    summarize_surveys()

    print(f"Encuestas insertadas en customer_surveys: {surveys_inserted}")
    print(f"Reviews generadas para API: {len(api_reviews)}")
    print(f"Archivo API seed: {API_SEED_PATH}")


if __name__ == "__main__":
    main()