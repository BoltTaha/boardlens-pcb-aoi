# API guide

Run `uvicorn boardlens.main:app --app-dir backend --reload`. Interactive OpenAPI is available at `/docs`.

Core routes: `/health`, `/ready`, `/models`, `/products`, `/inspections`, `/inspections/{id}`, `/inspections/{id}/review`, `/analytics/overview`, `/analytics/defects`, `/analytics/performance`, and `/system/status`.

`POST /inspections` is multipart form data with `product` (`pcb1`…`pcb4`) and `file` (JPEG/PNG/WebP). A missing model produces a persisted `REVIEW`; no synthetic inference is generated.

