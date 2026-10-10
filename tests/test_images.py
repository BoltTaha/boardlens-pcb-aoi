from pathlib import Path

import pytest
from boardlens.services.images import safe_artifact_path


def test_safe_artifact_path(tmp_path: Path):
    path = safe_artifact_path(tmp_path, "uploads", "abc-123", ".png")
    assert path == (tmp_path / "uploads" / "abc-123.png").resolve()


def test_rejects_unsafe_identifier(tmp_path: Path):
    with pytest.raises(ValueError):
        safe_artifact_path(tmp_path, "uploads", "../escape", ".png")
