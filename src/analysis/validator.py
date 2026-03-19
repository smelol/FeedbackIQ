ALLOWED_SENTIMENTS = {"positive", "negative", "neutral"}
ALLOWED_CATEGORIES = {
    "producto",
    "servicio",
    "ambiente",
    "precio",
    "limpieza",
    "otro",
}


def validate_analysis(data: dict) -> dict:
    sentiment = data.get("sentiment")
    categories = data.get("categories")
    summary = data.get("summary")
    urgency = data.get("urgency")

    if sentiment not in ALLOWED_SENTIMENTS:
        raise ValueError("Invalid sentiment")

    if not isinstance(categories, list):
        raise ValueError("Categories must be list")

    categories = [c for c in categories if c in ALLOWED_CATEGORIES]

    if not categories:
        categories = ["otro"]

    if not isinstance(summary, str):
        raise ValueError("Invalid summary")

    summary = summary[:100]

    if not isinstance(urgency, int) or not (1 <= urgency <= 5):
        raise ValueError("Invalid urgency")

    return {
        "sentiment": sentiment,
        "categories": categories,
        "summary": summary,
        "urgency": urgency,
    }