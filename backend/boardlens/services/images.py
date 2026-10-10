import io
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_PIXELS = 40_000_000


@dataclass(frozen=True)
class ValidatedImage:
    data: bytes
    image: Image.Image
    suffix: str


async def validate_upload(file: UploadFile, max_bytes: int) -> ValidatedImage:
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(415, detail="Only JPEG, PNG, and WebP images are accepted")
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(413, detail=f"Image exceeds {max_bytes} byte limit")
    if not data:
        raise HTTPException(400, detail="Empty image upload")
    try:
        image = Image.open(io.BytesIO(data))
        image.verify()
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(400, detail="Image cannot be decoded") from exc
    if image.width * image.height > MAX_PIXELS:
        raise HTTPException(413, detail="Decoded image dimensions are too large")
    suffix = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}[file.content_type]
    return ValidatedImage(data=data, image=image, suffix=suffix)


def safe_artifact_path(root: Path, category: str, identifier: str, suffix: str) -> Path:
    if not identifier.replace("-", "").isalnum():
        raise ValueError("unsafe artifact identifier")
    base = (root / category).resolve()
    base.mkdir(parents=True, exist_ok=True)
    target = (base / f"{identifier}{suffix}").resolve()
    if base not in target.parents:
        raise ValueError("artifact path escaped root")
    return target
