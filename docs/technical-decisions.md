# Technical decisions

## ADR-001 — Anomalib PatchCore for the anomaly branch

**Decision:** use Anomalib 2.6.2 PatchCore with a ResNet-18 backbone, explicit 224×224 preprocessing, and a 0.1% starting coreset on this CPU-only host.

**Evidence:** PatchCore is a memory-bank method: normal patch embeddings are collected, coreset sampled, and queried by nearest-neighbor distance. There is no gradient optimizer. The smaller backbone/resolution is a resource-aware baseline, not an accuracy claim. Final settings must be evaluated separately on PCB1–PCB4.

## ADR-002 — Detector remains conditional

VisA supplies pixel masks and a multi-class mask mapping, but semantic mask validity must be audited before training a class detector. A mask-to-box utility exists only for a clearly named `binary_anomaly` localization experiment. It does not turn regions into semantic defect labels.

YOLOv6 is Apache-2.0 and supports ONNX/OpenVINO deployment, but its upstream workflow and dependency surface are older than the actively maintained Ultralytics stack. BoardLens preserves a YOLOv6 experiment path because of the project goal, while deferring selection until annotations and a GPU training environment are available. Ultralytics is operationally easier but its AGPL/commercial licensing must be reviewed for any client deployment.

## ADR-003 — Modular monolith

A single FastAPI service is sufficient for this proof of concept. Offline fitting/evaluation scripts are separate processes. This avoids premature distributed-system complexity while keeping adapters replaceable.

## ADR-004 — Conservative missing-model behavior

An inspection with an absent or unloadable required model is persisted as `REVIEW` with an explicit reason. The service never emits fabricated scores or a misleading `PASS`.

## ADR-005 — Thresholds are configuration, not confidence blending

Product-specific review/fail thresholds are versioned. PCB1 now uses a deterministic calibration half and reports results on the held-out half; its high false-positive rate prevents release use. PCB2–PCB4 remain explicitly uncalibrated. A stronger release protocol must reserve validation data separately from the official test benchmark and report false-reject/missed-defect trade-offs.
