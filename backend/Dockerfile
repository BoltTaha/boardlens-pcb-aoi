FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY backend ./backend
COPY alembic.ini ./
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu \
      torch==2.14.1 torchvision==0.29.1 torchcodec==0.17.0 \
    && pip install --no-cache-dir '.[ml]'
COPY configs ./configs
RUN mkdir -p /app/artifacts
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn boardlens.main:app --app-dir backend --host 0.0.0.0 --port 8000"]
