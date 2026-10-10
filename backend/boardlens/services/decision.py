from dataclasses import dataclass

from boardlens.schemas import Decision, Detection


@dataclass(frozen=True)
class DecisionThresholds:
    review: float
    fail: float
    minimum_region_pixels: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.review <= self.fail:
            raise ValueError("thresholds must satisfy 0 <= review <= fail")


@dataclass(frozen=True)
class DecisionResult:
    decision: Decision
    reasons: list[str]


def decide(
    anomaly_score: float | None,
    detections: list[Detection],
    thresholds: DecisionThresholds,
    localized_pixels: int | None = None,
    model_available: bool = True,
) -> DecisionResult:
    if not model_available or anomaly_score is None:
        return DecisionResult(Decision.REVIEW, ["Required anomaly model is unavailable."])
    if anomaly_score < 0:
        return DecisionResult(Decision.REVIEW, ["Anomaly score is outside the calibrated range."])
    high_confidence = [d for d in detections if d.confidence >= thresholds.fail]
    if high_confidence:
        labels = ", ".join(sorted({d.label for d in high_confidence}))
        return DecisionResult(Decision.FAIL, [f"High-confidence detection: {labels}."])
    if anomaly_score >= thresholds.fail:
        return DecisionResult(
            Decision.FAIL,
            [f"Anomaly score {anomaly_score:.3f} meets fail threshold {thresholds.fail:.3f}."],
        )
    if localized_pixels is not None and 0 < localized_pixels < thresholds.minimum_region_pixels:
        return DecisionResult(
            Decision.REVIEW, ["Localized region is below the validated size limit."]
        )
    if detections or anomaly_score >= thresholds.review:
        return DecisionResult(
            Decision.REVIEW,
            [f"Evidence is between review and fail thresholds (score {anomaly_score:.3f})."],
        )
    return DecisionResult(
        Decision.PASS,
        [f"Anomaly score {anomaly_score:.3f} is below review threshold {thresholds.review:.3f}."],
    )
