FROM node:26.13.1-bookworm-slim AS frontend
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/index.html apps/web/monitor.html apps/web/tsconfig.json apps/web/vite.config.ts ./
COPY apps/web/src ./src
COPY docs/ui/shared/tokens.css /docs/ui/shared/tokens.css
RUN npm run build

FROM python:3.14.10-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.11.1 /uv /usr/local/bin/uv
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY services/monitor-service/pyproject.toml services/monitor-service/uv.lock ./
COPY services/monitor-service/src ./src
RUN uv sync --locked --no-dev
COPY --from=frontend /web/dist ./src/monitor_service/web
RUN cp src/monitor_service/web/monitor.html src/monitor_service/web/index.html
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "monitor_service.bootstrap:app", "--host", "0.0.0.0", "--port", "8000"]
