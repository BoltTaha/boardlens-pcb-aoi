import pytest
from boardlens.schemas import Decision, Detection
from boardlens.services.decision import DecisionThresholds, decide


@pytest.fixture
def thresholds():
    return DecisionThresholds(review=0.4, fail=0.7, minimum_region_pixels=10)


def test_pass_below_review(thresholds):
    assert decide(0.39, [], thresholds).decision == Decision.PASS


def test_review_at_boundary(thresholds):
    assert decide(0.4, [], thresholds).decision == Decision.REVIEW


def test_fail_at_boundary(thresholds):
    assert decide(0.7, [], thresholds).decision == Decision.FAIL


def test_unavailable_model_is_review(thresholds):
    result = decide(None, [], thresholds, model_available=False)
    assert result.decision == Decision.REVIEW
    assert "unavailable" in result.reasons[0]


def test_high_confidence_detection_fails(thresholds):
    detection = Detection(label="binary_anomaly", confidence=0.9, box_xyxy=(1, 2, 3, 4))
    assert decide(0.1, [detection], thresholds).decision == Decision.FAIL


def test_invalid_threshold_order_rejected():
    with pytest.raises(ValueError):
        DecisionThresholds(review=0.8, fail=0.6)
