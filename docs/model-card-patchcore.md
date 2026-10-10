# Model card — BoardLens PatchCore PCB baseline

## Intended use

Product-specific visual anomaly screening for VisA PCB images in a portfolio proof of concept. Not certified for safety, regulatory acceptance, or unattended factory rejection.

## Model

Anomalib PatchCore 2.6.2, ImageNet-pretrained ResNet-18 feature extractor, `layer2`/`layer3`, nearest-neighbor anomaly scoring, 224×224 input, starting coreset ratio 0.001. Fitting constructs a memory bank from normal examples; it is not gradient training.

## Status and evaluation

PCB1 was genuinely fitted on 904 normal training images. The official 200-image test portion was deterministically divided by sorted even/odd index: 50 normal + 50 anomaly for calibration and the remaining 50 + 50 for held-out evaluation. This is not directly comparable to reporting metrics on the full official test set.

Anomalib on the full official test split reported image AUROC 0.83415 and pixel AUROC 0.98042. On the held-out half, BoardLens measured image AUROC 0.85840, pixel AUROC 0.97764, and pixel average precision 0.81636. A validation target of 95% defect recall selected a raw fail threshold of 13.72647; held-out recall was 0.92, false-negative rate 0.08, and false-positive rate 0.64 (TN 18, FP 32, FN 4, TP 46). The very high false-positive rate makes this a baseline, not a deployable operating point. Default Anomalib F1 values are retained in raw metadata but are not used as calibrated release claims.

Checkpoint size is 12,340,291 bytes with SHA-256 `acd642a8cb5485916d9be5815eb2f9c7017fa43bfbe2e2e5aa3fddef2b1b3992`.

## Limitations

Downsampling can erase tiny defects. PatchCore is alignment-sensitive and product-specific. Synthetic robustness tests do not substitute for production-camera validation. The VisA distribution cannot establish line speed, fixture repeatability, contamination behavior, long-term drift, or real factory defect prevalence.
