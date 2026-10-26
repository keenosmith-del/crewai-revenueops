FROM python:3.12.15-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OTEL_SDK_DISABLED=true CREWAI_TELEMETRY_ENABLED=false CREWAI_TRACING_ENABLED=false
WORKDIR /srv/revenueops/backend
COPY backend/requirements.txt backend/requirements-lock.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip install -c requirements-lock.txt -r requirements.txt && useradd --create-home --uid 10001 revenueops
COPY backend/app/ ./app/
COPY backend/alembic.ini ./
COPY backend/migrations/ ./migrations/
COPY data/ /srv/revenueops/data/
COPY docs/testing/*.json /srv/revenueops/docs/testing/
RUN mkdir -p /srv/revenueops/.runtime && chown -R revenueops:revenueops /srv/revenueops
USER revenueops
EXPOSE 5050
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5050"]
