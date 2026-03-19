from datetime import datetime, timedelta, UTC
import requests

from src.etl import transform_api_review_to_unified, insert_unified_review

API_BASE_URL = "http://127.0.0.1:8081"
LOCATION_IDS = range(1, 16)


def fetch_reviews_for_location(location_id: int, since_iso: str) -> list[dict]:
    response = requests.get(
        f"{API_BASE_URL}/api/reviews",
        params={
            "location_id": location_id,
            "since": since_iso,
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


def load_api_reviews():
    since = datetime.now(UTC) - timedelta(days=7)
    since_iso = since.isoformat()

    total_fetched = 0
    total_inserted = 0
    total_duplicates = 0
    failed_locations = []

    for location_id in LOCATION_IDS:
        try:
            api_reviews = fetch_reviews_for_location(location_id, since_iso)
        except requests.RequestException as exc:
            print(f"[ERROR] Local {location_id}: no se pudo consultar la API -> {exc}")
            failed_locations.append(location_id)
            continue

        print(f"Local {location_id}: {len(api_reviews)} reviews obtenidas")
        total_fetched += len(api_reviews)

        for api_review in api_reviews:
            unified_review = transform_api_review_to_unified(api_review)
            inserted = insert_unified_review(**unified_review)

            if inserted == 1:
                total_inserted += 1
            else:
                total_duplicates += 1

    result = {
        "fetched": total_fetched,
        "inserted": total_inserted,
        "duplicates": total_duplicates,
        "failed_locations": failed_locations,
    }

    print("\nResumen carga API -> unified_reviews")
    print(f"Total fetched: {result['fetched']}")
    print(f"Total inserted: {result['inserted']}")
    print(f"Total duplicates skipped: {result['duplicates']}")
    print(f"Failed locations: {len(result['failed_locations'])}")

    return result


if __name__ == "__main__":
    load_api_reviews()