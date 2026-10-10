# LinkedIn project description

I built **BoardLens**, a production-oriented PCB automated optical inspection proof of concept. It combines product-specific PatchCore anomaly localization with an optional supervised detection branch, an explainable PASS/FAIL/REVIEW engine, a versioned FastAPI inspection service, persistent history, and a React operator dashboard.

The project emphasizes the engineering work that demos often omit: official dataset provenance, leakage-safe splits, conservative missing-model behavior, upload hardening, threshold versioning, latency instrumentation, reproducible evaluation, and honest limitations. Results are published only from executed runs—no fabricated metrics or semantic labels.

## Published demo asset

The generated 29.77-second, 1920×1080 H.264 portfolio reel is available at `docs/assets/boardlens-linkedin-demo.mp4`. It uses genuine VisA samples, a real API inspection result, and measured benchmark artifacts. It is intentionally silent so narration or platform-native music can be added during posting.

Suggested post:

> I built BoardLens, an end-to-end PCB visual-inspection proof of concept using Anomalib PatchCore, FastAPI, React, and the official VisA dataset. The project covers dataset validation, real model fitting, pixel-level anomaly evidence, explainable PASS/FAIL/REVIEW decisions, persistent inspection history, and measured CPU inference performance. The PCB1 baseline achieved 0.8584 image AUROC and 0.9776 pixel AUROC on the documented held-out half—but also exposed a 64% false-positive rate at the selected operating threshold. That limitation is part of the result: this is an engineering baseline, not a claimed factory-ready deployment.

Suggested hashtags: `#ComputerVision #MachineVision #Manufacturing #MLOps #FastAPI #React #PyTorch`

## Demo video storyboard

1. Show the system status and selected PCB recipe.
2. Upload a held-out board image and explain input validation.
3. Reveal the original image, anomaly heatmap/mask, score, decision, and reasons.
4. Open the persisted record with model and threshold versions.
5. Compare quality trends while clarifying they are predicted outcomes, not verified factory defect rates.
6. Show the reproducible dataset audit and benchmark artifact.
7. Close with resource and production-validation limitations.
