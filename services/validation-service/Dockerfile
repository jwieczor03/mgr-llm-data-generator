FROM python:3.14.10-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:0.11.1 /uv /usr/local/bin/uv
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY services/validation-service/pyproject.toml services/validation-service/uv.lock ./
COPY services/validation-service/src ./src
RUN uv sync --locked --no-dev
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "validation_service.bootstrap:app", "--host", "0.0.0.0", "--port", "8000"]
