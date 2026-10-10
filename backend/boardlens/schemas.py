from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Decision(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW = "REVIEW"


class Detection(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    box_xyxy: tuple[float, float, float, float]


class InspectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product: str
    created_at: datetime
    decision: Decision
    anomaly_score: float | None
    model_id: str
    threshold_version: str
    reasons: list[str]
    detections: list[dict]
    latency_ms: float
    image_url: str
    overlay_url: str | None = None
    review_status: str | None = None
    review_note: str | None = None


class ReviewRequest(BaseModel):
    decision: Decision
    note: str = Field(min_length=1, max_length=2000)


class HealthResponse(BaseModel):
    status: str
    version: str


class ErrorResponse(BaseModel):
    error: str
    detail: str
