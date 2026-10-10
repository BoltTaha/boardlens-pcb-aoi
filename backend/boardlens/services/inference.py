from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass
class InferenceOutput:
    anomaly_score: float | None
    detections: list[dict]
    localized_pixels: int | None
    overlay: Image.Image | None
    model_available: bool


class ModelUnavailableError(RuntimeError):
    pass


class InferenceService:
    """Lazy adapter boundary for genuine model artifacts; no synthetic predictions."""

    def __init__(self, model_root: Path) -> None:
        self.model_root = model_root
        self._models: dict[str, tuple[object, object]] = {}

    def _load(self, model_id: str) -> tuple[object, object]:
        if model_id in self._models:
            return self._models[model_id]
        checkpoint = self.model_root / f"{model_id}.ckpt"
        if not checkpoint.exists():
            raise ModelUnavailableError(f"Model artifact is unavailable: {model_id}")
        try:
            from anomalib.engine import Engine
            from anomalib.models import Patchcore

            # This loads a pickle-based Lightning checkpoint. Only locally fitted, trusted artifacts
            # may be configured here; externally supplied checkpoints are not accepted by the API.
            model = Patchcore.load_from_checkpoint(
                checkpoint,
                map_location="cpu",
                weights_only=False,
                pre_trained=False,
            )
            engine = Engine(accelerator="cpu", devices=1, logger=False, enable_progress_bar=False)
        except Exception as exc:
            raise ModelUnavailableError(f"Could not load model {model_id}") from exc
        self._models[model_id] = (model, engine)
        return model, engine

    @staticmethod
    def _overlay(image: Image.Image, anomaly_map: np.ndarray) -> Image.Image:
        low, high = np.percentile(anomaly_map, [5, 99])
        normalized = np.clip((anomaly_map - low) / max(high - low, 1e-8), 0, 1)
        heat = np.zeros((*normalized.shape, 4), dtype=np.uint8)
        heat[..., 0] = 255
        heat[..., 1] = (180 * normalized).astype(np.uint8)
        heat[..., 3] = (170 * normalized).astype(np.uint8)
        overlay = Image.fromarray(heat, "RGBA").resize(image.size, Image.Resampling.BILINEAR)
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    def inspect(self, image: Image.Image, image_path: Path, model_id: str) -> InferenceOutput:
        checkpoint = self.model_root / f"{model_id}.ckpt"
        if not checkpoint.exists():
            return InferenceOutput(None, [], None, None, False)
        try:
            model, engine = self._load(model_id)
            batches = engine.predict(
                model=model,
                data_path=image_path,
                return_predictions=True,
            )
            batch = batches[0]
            score = float(batch.pred_score[0].detach().cpu())
            anomaly_map = batch.anomaly_map[0].detach().cpu().numpy()
            return InferenceOutput(
                anomaly_score=score,
                detections=[],
                localized_pixels=None,
                overlay=self._overlay(image, anomaly_map),
                model_available=True,
            )
        except Exception as exc:
            raise ModelUnavailableError(f"Inference failed for {model_id}") from exc
