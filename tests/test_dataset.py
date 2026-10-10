import csv
from pathlib import Path

from PIL import Image

from ml.datasets.validate_visa import validate_original


def test_dataset_validator_detects_valid_minimal_tree(tmp_path: Path):
    root = tmp_path / "VisA"
    category = root / "pcb1"
    image = category / "Data/Images/Normal/000.JPG"
    image.parent.mkdir(parents=True)
    Image.new("RGB", (8, 8)).save(image)
    with (category / "image_anno.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image", "label"])
        writer.writeheader()
        writer.writerow({"image": "pcb1/Data/Images/Normal/000.JPG", "label": "normal"})
    report = validate_original(root, ("pcb1",))
    assert report["valid"] is True
    assert report["categories"]["pcb1"]["annotations"] == 1
