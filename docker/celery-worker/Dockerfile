FROM python:3.13-slim-bookworm
LABEL authors="e1_m"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/app/.venv/bin:/root/.local/bin/:$PATH"

COPY pyproject.toml ./
RUN uv sync

COPY src/celery_ src