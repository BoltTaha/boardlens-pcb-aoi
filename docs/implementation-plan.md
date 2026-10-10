# Implementation plan and execution checklist

Status legend: `[x]` implemented/verified, `[~]` implemented but awaiting real artifact or integration, `[ ]` not executed.

## Phase 1 — Environment and dataset

- [x] Inspect OS, CPU, memory, Python, Node, Docker, GPU, and disk.
- [x] Verify official VisA source, structure, counts, split utility, and CC BY 4.0 license.
- [x] Download and extract the official 1.93 GB archive; record size and local SHA-256.
- [x] Add integrity/format validation and official-split preparation scripts.
- [x] Generate final official-split manifests/statistics and authentic sample visualization.

## Phase 2 — anomaly baseline

- [x] Implement Anomalib PatchCore fit/evaluate entry point.
- [x] Fit PCB1, generate a genuine checkpoint/heatmaps, and report full-test plus held-out metrics.
- [ ] Repeat per PCB2–PCB4.
- [x] Calibrate PCB1 image thresholds on a deterministic validation half; document poor FPR.

## Phase 3 — supervised detection

- [x] Document YOLOv6 versus maintained alternatives.
- [x] Implement clearly labeled binary mask-to-box conversion.
- [ ] Audit semantic mask IDs and split suitability.
- [ ] Fine-tune/evaluate a detector on appropriate hardware.

## Phase 4 — backend

- [x] Implement upload validation, persistence, decision rules, history, review, analytics, and status APIs.
- [x] Connect and smoke-test the genuine PCB1 PatchCore runtime.
- [ ] Apply Alembic migration to PostgreSQL integration environment.

## Phase 5 — frontend

- [x] Implement API-connected inspection/history/analytics/model/configuration views.
- [x] Validate genuine heatmap/overlay generation and API artifact serving.
- [ ] Add triggered video-file inspection.

## Phase 6/7 — benchmark, deployment, polish

- [x] Add benchmark/robustness entry points and run a 20-sample warm API benchmark.
- [x] Add Docker packaging and Compose topology.
- [x] Export genuine PCB1 accuracy, latency, and controlled-robustness JSON.
- [~] Capture authentic dataset/model overlays; polished browser screenshots remain pending.
- [ ] Build and launch the full PostgreSQL Compose stack on this host.
