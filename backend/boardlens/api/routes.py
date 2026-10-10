import time
import uuid
from pathlib import Path

import yaml
from boardlens.core.config import get_settings
from boardlens.db.base import Inspection, SessionLocal
from boardlens.schemas import HealthResponse, InspectionRead, ReviewRequest
from boardlens.services.decision import DecisionThresholds, decide
from boardlens.services.images import safe_artifact_path, validate_upload
from boardlens.services.inference import InferenceService, ModelUnavailableError
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

router = APIRouter()
settings = get_settings()
inference = InferenceService(settings.artifact_root / "models")


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def to_schema(item: Inspection) -> InspectionRead:
    return InspectionRead(
        id=item.id,
        product=item.product,
        created_at=item.created_at,
        decision=item.decision,
        anomaly_score=item.anomaly_score,
        model_id=item.model_id,
        threshold_version=item.threshold_version,
        reasons=item.reasons,
        detections=item.detections,
        latency_ms=item.latency_ms,
        image_url=f"/artifacts/uploads/{Path(item.image_path).name}",
        overlay_url=(
            f"/artifacts/overlays/{Path(item.overlay_path).name}" if item.overlay_path else None
        ),
        review_status=item.review_status,
        review_note=item.review_note,
    )


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")


@router.get("/ready")
async def ready() -> dict:
    model_cfg = load_yaml(settings.model_config_path)
    available = []
    for model_id, model in model_cfg.get("models", {}).items():
        artifact = Path(model.get("artifact", ""))
        if model.get("status") == "ready" and artifact.is_file():
            available.append(model_id)
    return {"status": "ready" if available else "degraded", "available_models": available}


@router.get("/models")
async def models() -> dict:
    return load_yaml(settings.model_config_path)


@router.get("/products")
async def products() -> dict:
    return load_yaml(settings.product_config)


@router.post("/inspections", response_model=InspectionRead, status_code=201)
async def create_inspection(
    product: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> InspectionRead:
    products_cfg = load_yaml(settings.product_config)
    product_cfg = products_cfg.get("products", {}).get(product)
    if not product_cfg:
        raise HTTPException(422, detail="Unknown product configuration")
    validated = await validate_upload(file, settings.max_upload_bytes)
    inspection_id = str(uuid.uuid4())
    image_path = safe_artifact_path(
        settings.artifact_root, "uploads", inspection_id, validated.suffix
    )
    image_path.write_bytes(validated.data)
    start = time.perf_counter()
    model_id = product_cfg["anomaly_model"]
    try:
        output = inference.inspect(validated.image, image_path, model_id)
    except ModelUnavailableError as exc:
        raise HTTPException(503, detail="Configured inspection model could not run") from exc
    thresholds = DecisionThresholds(**product_cfg["thresholds"])
    decision = decide(
        output.anomaly_score, [], thresholds, output.localized_pixels, output.model_available
    )
    latency_ms = (time.perf_counter() - start) * 1000
    overlay_path = None
    if output.overlay is not None:
        overlay_path = safe_artifact_path(settings.artifact_root, "overlays", inspection_id, ".jpg")
        output.overlay.save(overlay_path, format="JPEG", quality=92)
    item = Inspection(
        id=inspection_id,
        product=product,
        decision=decision.decision.value,
        anomaly_score=output.anomaly_score,
        model_id=model_id,
        threshold_version=products_cfg.get("version", "unknown"),
        reasons=decision.reasons,
        detections=output.detections,
        latency_ms=latency_ms,
        image_path=str(image_path),
        overlay_path=str(overlay_path) if overlay_path else None,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_schema(item)


@router.get("/inspections", response_model=list[InspectionRead])
async def list_inspections(
    decision: str | None = None,
    product: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[InspectionRead]:
    query = select(Inspection).order_by(Inspection.created_at.desc()).limit(limit)
    if decision:
        query = query.where(Inspection.decision == decision.upper())
    if product:
        query = query.where(Inspection.product == product)
    return [to_schema(item) for item in db.scalars(query)]


@router.get("/inspections/{inspection_id}", response_model=InspectionRead)
async def get_inspection(inspection_id: str, db: Session = Depends(get_db)) -> InspectionRead:
    item = db.get(Inspection, inspection_id)
    if not item:
        raise HTTPException(404, detail="Inspection not found")
    return to_schema(item)


@router.post("/inspections/{inspection_id}/review", response_model=InspectionRead)
async def review_inspection(
    inspection_id: str, review: ReviewRequest, db: Session = Depends(get_db)
) -> InspectionRead:
    item = db.get(Inspection, inspection_id)
    if not item:
        raise HTTPException(404, detail="Inspection not found")
    item.review_status = review.decision.value
    item.review_note = review.note
    db.commit()
    db.refresh(item)
    return to_schema(item)


@router.get("/analytics/overview")
async def analytics_overview(db: Session = Depends(get_db)) -> dict:
    total = db.scalar(select(func.count()).select_from(Inspection)) or 0
    rows = db.execute(select(Inspection.decision, func.count()).group_by(Inspection.decision)).all()
    counts = {decision: count for decision, count in rows}
    return {"total": total, "decisions": counts, "source": "recorded_inspections"}


@router.get("/analytics/defects")
async def analytics_defects() -> dict:
    return {"classes": [], "note": "No validated semantic detection model is installed."}


@router.get("/analytics/performance")
async def analytics_performance(db: Session = Depends(get_db)) -> dict:
    values = list(db.scalars(select(Inspection.latency_ms)))
    values.sort()
    if not values:
        return {"samples": 0, "p50_ms": None, "p95_ms": None, "p99_ms": None}

    def pct(q: float) -> float:
        return values[min(len(values) - 1, round((len(values) - 1) * q))]

    return {"samples": len(values), "p50_ms": pct(0.5), "p95_ms": pct(0.95), "p99_ms": pct(0.99)}


@router.get("/system/status")
async def system_status() -> dict:
    return {"environment": settings.env, "database": "configured", "models": await ready()}
