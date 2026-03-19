from src.alerts.rules import (
    detect_critical_reviews,
    detect_negative_spike_24h,
    detect_low_weekly_average,
)
from src.alerts.repository import insert_alert
from src.alerts.notifier import notify_alert


def run_alert_detection():
    all_candidates = []
    all_candidates.extend(detect_critical_reviews())
    all_candidates.extend(detect_negative_spike_24h())
    all_candidates.extend(detect_low_weekly_average())

    print(f"Alertas candidatas detectadas: {len(all_candidates)}")

    inserted_count = 0
    skipped_count = 0

    for alert in all_candidates:
        inserted = insert_alert(
            severity=alert["severity"],
            location_id=alert["location_id"],
            rule_code=alert["rule_code"],
            message=alert["message"],
            dedupe_key=alert["dedupe_key"],
        )

        if inserted == 1:
            notify_alert(alert)
            inserted_count += 1
        else:
            skipped_count += 1

    print("\nResumen alertas:")
    print(f"✔ nuevas alertas: {inserted_count}")
    print(f"➖ duplicadas ignoradas: {skipped_count}")