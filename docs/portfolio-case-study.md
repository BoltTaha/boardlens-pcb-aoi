# BoardLens portfolio case study

## Problem

PCB inspection needs traceable evidence, localized anomaly output, and conservative failure handling—not only a classifier score.

## Dataset and approach

BoardLens uses the officially licensed VisA PCB subsets and preserves their published anomaly-detection split. A product-specific PatchCore branch localizes deviations from normal boards. A supervised detector is an optional second branch only when defensible annotations and compute exist.

## Architecture and evaluation

Offline training and benchmarking are isolated from a FastAPI inspection service and React operator dashboard. Every inspection records model/threshold versions and explainable reasons. Evaluation covers image/pixel metrics and staged latency; claims remain blank until the corresponding run artifact exists.

The executed PCB1 baseline fitted PatchCore on 904 normal images. On the 100-image held-out half used for thresholded evaluation, it reached image AUROC 0.8584, pixel AUROC 0.9776, pixel AP 0.8164, and defect recall 0.92. The same operating threshold yielded a 0.64 false-positive rate, making alignment and threshold improvement the key technical finding rather than a production-readiness claim. Warm in-process API latency on the i5-7300U was 385 ms p50 and 495 ms p95 over 20 measured requests after three warm-ups.

## Business relevance

The design demonstrates how an AOI proof of concept can evolve toward line integration: explicit product recipes, review states, audit history, versioned models, threshold governance, and failure-safe operation. It is not marketed as a certified production deployment.
