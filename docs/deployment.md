# Deployment

## Local development

Create `.env` from `.env.example`, install dependencies, apply migrations with `alembic upgrade head`, then run the API and Vite commands in the README. SQLite is a development convenience only.

## Docker Compose

`docker compose up --build` starts PostgreSQL 17, applies Alembic migrations, starts FastAPI, and serves the compiled dashboard through Nginx on port 8080. PostgreSQL and inspection artifacts use named persistent volumes. Set a unique `POSTGRES_PASSWORD` in the ignored `.env` file before running Docker Compose; startup intentionally fails when it is missing or empty.

Stop cleanly with `docker compose down`. This preserves named volumes; adding `--volumes` removes persistent data and should be treated as destructive.

Model weights are deliberately excluded from source control. Mount validated artifacts under `/app/artifacts/models` and update `configs/models.yaml` with status and metadata. A model is not ready merely because a file exists.

## Production gaps

Add TLS/reverse-proxy policy, authentication/authorization, secrets management, object storage, database backup/restore drills, monitoring, worker isolation, signed model artifacts, and line-specific acceptance testing before considering a factory deployment.
