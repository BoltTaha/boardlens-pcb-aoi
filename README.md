# BoardLens

BoardLens is a production-oriented PCB automated optical inspection proof of concept: official VisA data preparation, product-specific Anomalib PatchCore fitting, an explainable inspection engine, traceable REST API, persistent history, and an API-connected React dashboard.

> Current status: the application/data pipelines and a genuine PCB1 PatchCore baseline are implemented and verified. PCB1 metrics below come from saved run artifacts; PCB2–PCB4 and the detector remain untrained. Missing models return `REVIEW`, never a fake score. This is not a certified production-line system.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
uvicorn boardlens.main:app --app-dir backend --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Dataset and PatchCore

```bash
bash scripts/bootstrap_data.sh
pip install --index-url https://download.pytorch.org/whl/cpu \
  torch==2.14.1 torchvision==0.29.1 torchcodec==0.17.0
pip install -e '.[ml]'
python -m ml.anomaly.fit_patchcore --data-root data/processed/visa --category pcb1
```

The official VisA archive is 1,929,840,640 bytes and is ignored by Git. The preparation command uses the upstream 1-class split. PatchCore “fit” means normal feature extraction and memory-bank coreset construction, not backpropagation.

The executed PCB1 baseline used 904 normal training images, ResNet-18 features, 224×224 input, and a 0.001 coreset. Its held-out-half image AUROC was 0.8584 and pixel AUROC 0.9776, but the validation-selected threshold produced a 0.64 false-positive rate. Treat it as an engineering baseline, not an acceptable production operating point.

## Tests

```bash
pip install -e '.[dev]'
pytest
ruff check backend ml tests
cd frontend && npm ci && npm run build
```

## Deployment

```bash
cp .env.example .env
docker compose up --build
```

See [architecture](docs/architecture.md), [technical decisions](docs/technical-decisions.md), [dataset audit](docs/dataset-audit.md), [implementation checklist](docs/implementation-plan.md), [API guide](docs/api.md), [benchmark report](docs/benchmark-report.md), [deployment guide](docs/deployment.md), [troubleshooting](docs/troubleshooting.md), [portfolio case study](docs/portfolio-case-study.md), and [limitations](docs/limitations.md).
