import json
from pathlib import Path

ALERTS_LOG_PATH = Path("data/alerts_log.jsonl")


def notify_alert(alert: dict):
    ALERTS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with ALERTS_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(alert, ensure_ascii=False) + "\n")