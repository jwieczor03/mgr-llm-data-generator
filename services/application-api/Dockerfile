FROM node:26.13.1-bookworm-slim AS frontend
WORKDIR /web
COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm ci
COPY apps/web/index.html apps/web/tsconfig.json apps/web/vite.config.ts ./
COPY apps/web/src ./src
RUN npm run build

FROM python:3.14.10-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.11.1 /uv /usr/local/bin/uv
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY services/application-api/pyproject.toml services/application-api/uv.lock ./
COPY services/application-api/src ./src
RUN uv sync --locked --no-dev
COPY --from=frontend /web/dist ./src/application_api/web
RUN mkdir -p /var/lib/application-api/project /var/lib/application-api/working \
    && chown 10001:10001 /var/lib/application-api/project /var/lib/application-api/working
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "application_api.bootstrap:app", "--host", "0.0.0.0", "--port", "8000"]
