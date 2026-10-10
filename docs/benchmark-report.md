# Benchmark report

## Methodology

All model timing runs require warm-up, fixed batch size/input resolution/backend, and hardware metadata. Report p50/p95/p99 only with enough samples. Accuracy is per task: image/pixel anomaly metrics for PatchCore and mAP/precision/recall for a supervised detector. Different tasks are not ranked by a single universal score.

## Executed results

Dataset integrity validation completed: 4,416 RGB PCB images and 400 masks decoded with zero missing/corrupt references.

PCB1 PatchCore was fitted on 904 normal images using CPU, 224×224 input, ResNet-18 features, and a 0.001 coreset. Anomalib's full official test evaluation reported image AUROC 0.83415 and pixel AUROC 0.98042. For threshold calibration, sorted even indices from the official test portion (50 normal, 50 anomalous) were used as validation; odd indices (50 + 50) remained held out. The held-out metrics were image AUROC 0.85840, pixel AUROC 0.97764, pixel AP 0.81636, defect recall 0.92, FPR 0.64, FNR 0.08, and precision 0.58974. Confusion counts were TN 18, FP 32, FN 4, TP 46.

The high FPR is a failed industrial operating point even though ranking/localization AUROC is promising. Alignment, input resolution, coreset size, and threshold policy need further experiments. No detector benchmark is claimed.

Warm API latency was measured for 20 batch-size-one inspections after 3 warm-ups on the documented i5-7300U CPU. The in-process ASGI wall time (upload validation, artifact writes, inference, overlay generation, and SQLite persistence; no network transport) was p50 384.97 ms, p95 495.30 ms, and p99 627.21 ms. The model/orchestration segment was p50 350.31 ms, p95 452.87 ms, and p99 583.36 ms. Process peak RSS was 722.5 MiB; GPU memory is not applicable. Twenty samples are enough to exercise the reporter but too few for a stable production tail-latency claim.

## Required anomaly metrics

The release report will include image AUROC, pixel AUROC, pixel average precision, defect recall, false-positive rate, false-negative rate, and a confusion matrix at validation-calibrated thresholds. Test data must not select that threshold.

## Robustness protocol

`ml/evaluation/robustness_benchmark.py` generates and evaluates controlled brightness, contrast, blur, noise, rotation, translation, scale, and partial-occlusion variants. Results from these synthetic perturbations must be labeled as controlled robustness tests, not production-camera validation.

A seeded controlled run used 10 normal and 10 anomalous PCB1 images per condition at the calibrated fail threshold. Baseline recall/FPR were 0.90/0.60. Brightness, contrast, and Gaussian noise retained 0.90 recall, with FPR 0.50, 0.30, and 0.70 respectively. Blur produced 1.00 recall/0.60 FPR. Two-degree rotation, 0.95 scale, and partial occlusion each drove FPR to 1.00; a 6 px/−4 px translation drove FPR to 0.80. The small sample and synthetic changes are diagnostic only, but they clearly demonstrate alignment sensitivity and reinforce that the current baseline is not production-ready.
