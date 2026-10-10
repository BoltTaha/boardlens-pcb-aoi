import asyncio
import io

import httpx
from boardlens.db.base import init_db
from boardlens.main import app
from PIL import Image


def request(method: str, path: str, **kwargs) -> httpx.Response:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, path, **kwargs)

    init_db()
    return asyncio.run(run())


def test_health():
    response = request("GET", "/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_unknown_product_rejected():
    response = request(
        "POST",
        "/inspections",
        data={"product": "unknown"},
        files={"file": ("board.png", b"not-used", "image/png")},
    )
    assert response.status_code == 422


def test_corrupt_image_rejected():
    response = request(
        "POST",
        "/inspections",
        data={"product": "pcb2"},
        files={"file": ("board.png", b"not-an-image", "image/png")},
    )
    assert response.status_code == 400


def test_missing_model_persists_review():
    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), "green").save(buffer, format="PNG")
    response = request(
        "POST",
        "/inspections",
        data={"product": "pcb2"},
        files={"file": ("board.png", buffer.getvalue(), "image/png")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["decision"] == "REVIEW"
    assert body["anomaly_score"] is None
