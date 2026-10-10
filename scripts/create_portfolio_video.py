#!/usr/bin/env python3
"""Create a silent LinkedIn-ready BoardLens proof-of-concept reel."""

from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "assets" / "boardlens-linkedin-demo.mp4"
FRAME_DIR = ROOT / "artifacts" / "video-frames"
W, H = 1920, 1080
INK = "#171a17"
MUTED = "#687168"
GREEN = "#0d6035"
GREEN_2 = "#18864b"
GREEN_SOFT = "#eaf6ef"
BG = "#f4f5f1"
WHITE = "#ffffff"
LINE = "#dfe3dc"
AMBER = "#a7650b"
AMBER_SOFT = "#fff7e8"
RED = "#b93636"
RED_SOFT = "#fff0ef"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{name}", size)


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (W, H), BG)
    return image, ImageDraw.Draw(image)


def header(draw: ImageDraw.ImageDraw, section: str) -> None:
    draw.rounded_rectangle((70, 48, 118, 96), 12, fill=INK)
    draw.ellipse((84, 62, 104, 82), outline=WHITE, width=3)
    draw.text((136, 50), "BoardLens", font=font(30, True), fill=INK)
    draw.text((138, 84), "PCB AOI PROOF OF CONCEPT", font=font(12, True), fill=MUTED)
    draw.text((1680, 62), section.upper(), font=font(15, True), fill=GREEN, anchor="ra")
    draw.line((70, 125, 1850, 125), fill=LINE, width=2)


def title(draw: ImageDraw.ImageDraw, eyebrow: str, heading: str, subheading: str) -> None:
    draw.text((90, 180), eyebrow.upper(), font=font(16, True), fill=GREEN)
    draw.text((90, 220), heading, font=font(62, True), fill=INK)
    lines = wrap(subheading, 78)
    draw.multiline_text((92, 310), "\n".join(lines), font=font(24), fill=MUTED, spacing=12)


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int = 24) -> None:
    draw.rounded_rectangle(box, radius, fill=WHITE, outline=LINE, width=2)


def fit_image(source: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(source).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    target = Image.new("RGB", size, "#eef0eb")
    target.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return target


def metric(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, value: str, note: str) -> None:
    card(draw, (x, y, x + 390, y + 190))
    draw.rectangle((x, y, x + 390, y + 7), fill=GREEN_2)
    draw.text((x + 26, y + 28), label.upper(), font=font(14, True), fill=MUTED)
    draw.text((x + 26, y + 62), value, font=font(42, True), fill=INK)
    draw.text((x + 26, y + 132), note, font=font(16), fill=MUTED)


def latest_inspection() -> dict:
    db = sqlite3.connect(ROOT / "boardlens.db")
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT * FROM inspections ORDER BY created_at DESC LIMIT 1").fetchone()
    db.close()
    if row is None:
        raise RuntimeError("No recorded inspection is available")
    return dict(row)


def build_frames() -> list[Path]:
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    latency = json.loads((ROOT / "artifacts/results/api-latency-pcb1.json").read_text())
    evaluation = json.loads(
        (ROOT / "artifacts/results/patchcore-pcb1-v0-calibrated.json").read_text()
    )
    inspection = latest_inspection()
    frames: list[Path] = []

    image, draw = canvas()
    draw.rectangle((0, 0, 26, H), fill=GREEN_2)
    draw.text((120, 210), "BOARDLENS", font=font(23, True), fill=GREEN)
    draw.text((120, 275), "PCB inspection,\nmade traceable.", font=font(78, True), fill=INK, spacing=6)
    draw.text(
        (125, 500),
        "A working computer-vision proof of concept built on the official VisA dataset.",
        font=font(26),
        fill=MUTED,
    )
    draw.rounded_rectangle((125, 610, 500, 672), 31, fill=GREEN)
    draw.text((312, 641), "PATCHCORE • FASTAPI • REACT", font=font(16, True), fill=WHITE, anchor="mm")
    draw.text((125, 900), "REAL DATA  /  REAL CHECKPOINT  /  MEASURED RESULTS", font=font(16, True), fill=GREEN)
    draw.text((125, 950), "Portfolio proof of concept — not a certified factory deployment", font=font(15), fill=MUTED)
    path = FRAME_DIR / "01-intro.png"; image.save(path); frames.append(path)

    image, draw = canvas(); header(draw, "Dataset")
    title(draw, "Verified source data", "4,416 PCB images audited", "PCB1–PCB4 from the official VisA anomaly dataset, with 400 decoded pixel masks and zero missing or corrupt references.")
    montage = fit_image(ROOT / "docs/assets/visa_samples.png", (1060, 650))
    image.paste(montage, (760, 300))
    for y, value, label in [(510, "4,416", "RGB images"), (635, "400", "pixel masks"), (760, "0", "broken references")]:
        draw.text((110, y), value, font=font(48, True), fill=INK)
        draw.text((112, y + 58), label.upper(), font=font(14, True), fill=GREEN)
    path = FRAME_DIR / "02-dataset.png"; image.save(path); frames.append(path)

    image, draw = canvas(); header(draw, "Live result")
    draw.text((80, 165), "GENUINE PCB1 INSPECTION", font=font(16, True), fill=GREEN)
    draw.text((80, 205), "Original frame → anomaly evidence", font=font(46, True), fill=INK)
    original = fit_image(Path(inspection["image_path"]), (760, 570))
    overlay = fit_image(Path(inspection["overlay_path"]), (760, 570))
    card(draw, (70, 300, 850, 900)); card(draw, (890, 300, 1670, 900))
    image.paste(original, (80, 310)); image.paste(overlay, (900, 310))
    draw.text((90, 920), "ORIGINAL INPUT", font=font(14, True), fill=MUTED)
    draw.text((910, 920), "PATCHCORE HEATMAP", font=font(14, True), fill=GREEN)
    draw.rounded_rectangle((1700, 300, 1840, 350), 25, fill=AMBER_SOFT, outline="#efd8ad")
    draw.text((1770, 325), inspection["decision"], font=font(16, True), fill=AMBER, anchor="mm")
    draw.text((1700, 405), "SCORE", font=font(13, True), fill=MUTED)
    draw.text((1700, 438), f'{inspection["anomaly_score"]:.3f}', font=font(31, True), fill=INK)
    draw.text((1700, 510), "MODEL", font=font(13, True), fill=MUTED)
    draw.multiline_text((1700, 543), "patchcore-\npcb1-v0", font=font(18, True), fill=INK, spacing=5)
    draw.text((70, 1010), "Recorded through the real inspection API • Image and overlay persisted with model + threshold versions", font=font(17), fill=MUTED)
    path = FRAME_DIR / "03-inspection.png"; image.save(path); frames.append(path)

    image, draw = canvas(); header(draw, "Architecture")
    title(draw, "Explainable by design", "One inspection. Four traceable stages.", "The model output is never presented alone: every decision keeps its evidence, threshold version, model identity, and processing time.")
    stages = [(100, "01", "Image validation", "MIME, size, decoding"), (550, "02", "PatchCore", "Score + pixel map"), (1000, "03", "Decision rules", "PASS / FAIL / REVIEW"), (1450, "04", "Audit history", "Evidence + versions")]
    for x, number, name, note in stages:
        card(draw, (x, 570, x + 360, 800))
        draw.text((x + 28, 598), number, font=font(18, True), fill=GREEN)
        draw.text((x + 28, 655), name, font=font(25, True), fill=INK)
        draw.text((x + 28, 715), note, font=font(17), fill=MUTED)
        if x < 1450:
            draw.line((x + 370, 685, x + 430, 685), fill=GREEN_2, width=5)
            draw.polygon(((x + 430, 685), (x + 414, 675), (x + 414, 695)), fill=GREEN_2)
    draw.rounded_rectangle((100, 890, 870, 952), 12, fill=GREEN_SOFT)
    draw.text((125, 910), "Missing or incompatible models safely produce REVIEW — never a fabricated score.", font=font(17, True), fill=GREEN)
    path = FRAME_DIR / "04-architecture.png"; image.save(path); frames.append(path)

    metrics = evaluation["metrics"]
    image, draw = canvas(); header(draw, "Measured results")
    title(draw, "Executed on CPU", "An honest engineering baseline", "Measured on the documented i5-7300U host. The ranking and localization metrics are promising; the operating threshold still rejects too many normal boards.")
    metric(draw, 90, 520, "Image AUROC", f'{metrics["image_auroc"]:.4f}', "100-image held-out half")
    metric(draw, 510, 520, "Pixel AUROC", f'{metrics["pixel_auroc"]:.4f}', "Pixel localization")
    metric(draw, 930, 520, "Defect recall", f'{metrics["defect_recall"]:.0%}', "46 TP / 4 FN")
    metric(draw, 1350, 520, "Warm API p50", f'{latency["wall_ms"]["p50"]:.0f} ms', "20 measured requests")
    draw.rounded_rectangle((90, 775, 1740, 890), 18, fill=RED_SOFT, outline="#efc4c1")
    draw.text((125, 805), "KEY LIMITATION", font=font(14, True), fill=RED)
    draw.text((125, 842), "64% held-out false-positive rate — useful baseline, not a production operating point.", font=font(24, True), fill=INK)
    draw.text((90, 975), "No fabricated metrics • Full run artifacts are included in the repository", font=font(17), fill=MUTED)
    path = FRAME_DIR / "05-metrics.png"; image.save(path); frames.append(path)

    image, draw = canvas(); header(draw, "Portfolio")
    draw.text((100, 215), "FROM DATASET TO\nINSPECTION SYSTEM", font=font(65, True), fill=INK, spacing=6)
    draw.text((105, 405), "PatchCore anomaly detection", font=font(24, True), fill=GREEN)
    draw.text((105, 455), "FastAPI inspection and persistence", font=font(24, True), fill=GREEN)
    draw.text((105, 505), "React operator dashboard", font=font(24, True), fill=GREEN)
    draw.text((105, 555), "Threshold governance and benchmarking", font=font(24, True), fill=GREEN)
    card(draw, (1050, 220, 1780, 760))
    draw.text((1110, 280), "BOARDLENS", font=font(18, True), fill=GREEN)
    draw.text((1110, 330), "Industrial computer vision\nwith evidence, not hype.", font=font(39, True), fill=INK, spacing=8)
    draw.line((1110, 500, 1700, 500), fill=LINE, width=2)
    draw.text((1110, 550), "Built as a reproducible proof of concept", font=font(18), fill=MUTED)
    draw.text((1110, 600), "VisA • Anomalib • PyTorch • FastAPI • React", font=font(17, True), fill=INK)
    draw.rounded_rectangle((105, 830, 695, 905), 38, fill=GREEN)
    draw.text((400, 868), "OPEN TO MACHINE VISION OPPORTUNITIES", font=font(17, True), fill=WHITE, anchor="mm")
    draw.text((105, 965), "Portfolio demo • Actual source, tests, checkpoint and reports included", font=font(16), fill=MUTED)
    path = FRAME_DIR / "06-outro.png"; image.save(path); frames.append(path)
    return frames


def encode(frames: list[Path]) -> None:
    duration = 5.5
    transition = 0.65
    command = ["ffmpeg", "-y"]
    for frame in frames:
        command.extend(["-loop", "1", "-t", str(duration), "-i", str(frame)])
    command.extend(["-f", "lavfi", "-t", str(duration * len(frames)), "-i", "anullsrc=r=48000:cl=stereo"])
    filters = []
    for index in range(len(frames)):
        filters.append(f"[{index}:v]scale={W}:{H},setsar=1,fps=30[v{index}]")
    current = "v0"
    for index in range(1, len(frames)):
        output = f"x{index}"
        offset = (duration - transition) * index
        filters.append(
            f"[{current}][v{index}]xfade=transition=fade:duration={transition}:offset={offset:.2f}[{output}]"
        )
        current = output
    total = duration + (len(frames) - 1) * (duration - transition)
    command.extend(
        [
            "-filter_complex", ";".join(filters), "-map", f"[{current}]", "-map", f"{len(frames)}:a",
            "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "128k", str(OUTPUT),
        ]
    )
    subprocess.run(command, check=True)


def main() -> int:
    frames = build_frames()
    encode(frames)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
