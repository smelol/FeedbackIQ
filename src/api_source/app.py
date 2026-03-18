from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
from src.api_source.seed_data import build_api_reviews_seed

app = FastAPI(title="FeedbackIQ Reviews API")

API_REVIEWS = build_api_reviews_seed()


class ReviewResponse(BaseModel):
    review_id: str
    location_id: int
    rating: int
    text: str
    author: Optional[str]
    created_at: str


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@app.get("/api/reviews", response_model=list[ReviewResponse])
def get_reviews(
    location_id: int = Query(..., ge=1, le=15),
    since: datetime = Query(...)
):
    filtered_reviews = [
        review
        for review in API_REVIEWS
        if review["location_id"] == location_id
        and parse_iso_datetime(review["created_at"]) >= since
    ]

    return filtered_reviews