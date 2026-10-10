from datetime import UTC, datetime

from boardlens.core.config import get_settings
from sqlalchemy import JSON, DateTime, Float, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    product: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )
    decision: Mapped[str] = mapped_column(String(16), index=True)
    anomaly_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_id: Mapped[str] = mapped_column(String(128))
    threshold_version: Mapped[str] = mapped_column(String(64))
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    detections: Mapped[list] = mapped_column(JSON, default=list)
    latency_ms: Mapped[float] = mapped_column(Float)
    image_path: Mapped[str] = mapped_column(Text)
    overlay_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_status: Mapped[str | None] = mapped_column(String(16), nullable=True)
    review_note: Mapped[str | None] = mapped_column(Text, nullable=True)


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    Base.metadata.create_all(engine)
