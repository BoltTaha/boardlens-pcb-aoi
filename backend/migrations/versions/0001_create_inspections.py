"""Create inspections audit table."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inspections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decision", sa.String(16), nullable=False),
        sa.Column("anomaly_score", sa.Float(), nullable=True),
        sa.Column("model_id", sa.String(128), nullable=False),
        sa.Column("threshold_version", sa.String(64), nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.Column("detections", sa.JSON(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("image_path", sa.Text(), nullable=False),
        sa.Column("overlay_path", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(16), nullable=True),
        sa.Column("review_note", sa.Text(), nullable=True),
    )
    op.create_index("ix_inspections_product", "inspections", ["product"])
    op.create_index("ix_inspections_created_at", "inspections", ["created_at"])
    op.create_index("ix_inspections_decision", "inspections", ["decision"])


def downgrade() -> None:
    op.drop_table("inspections")
