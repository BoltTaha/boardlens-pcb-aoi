from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from boardlens.api.routes import router
from boardlens.core.config import get_settings
from boardlens.core.logging import configure_logging
from boardlens.db.base import init_db

settings = get_settings()
configure_logging()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="BoardLens Inspection API",
    version="0.1.0",
    description="Traceable PCB AOI proof-of-concept API; not a certified production-line system.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[v.strip() for v in settings.allowed_origins.split(",")],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
settings.artifact_root.mkdir(parents=True, exist_ok=True)
app.mount("/artifacts", StaticFiles(directory=settings.artifact_root), name="artifacts")
app.include_router(router)


@app.exception_handler(Exception)
async def unhandled_error(_request: Request, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500, content={"error": "internal_error", "detail": "Unexpected server error"}
    )
