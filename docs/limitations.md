# Limitations and future work

- This host has no NVIDIA GPU, only 2 physical CPU cores and 7.6 GiB RAM. Full detector fine-tuning is not responsible here.
- PCB1 is the only fitted product model. PCB2–PCB4 must be fitted and calibrated independently before inspection use.
- The PCB1 validation-selected operating point has a 0.64 held-out false-positive rate, so it is not suitable for factory acceptance decisions.
- Live camera support is not implemented; video replay would still need a product trigger to prevent duplicate counts.
- PostgreSQL is configured for Compose, but the full container stack was not launched; local automated tests and measured API runs use SQLite.
- No semantic detector is trained. Binary mask-derived boxes, if used, mean only “anomaly region.”
- PCB1 thresholds were selected on a deterministic 50-normal/50-anomaly calibration subset. The remaining 50/50 subset was held out, but both halves originate from VisA's official test portion; a stronger release protocol needs a purpose-built validation split or cross-validation.
- The 20-sample latency and 10+10-per-condition robustness runs are engineering diagnostics, not stable production performance estimates.
- VisA cannot validate production illumination, optics, conveyor motion, fixture tolerances, drift, or business defect rates.
