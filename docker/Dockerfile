# Build stage
FROM python:3.12-alpine AS build-stage

WORKDIR /usr/src/app

# Install build dependencies
RUN apk add --no-cache --update gcc libc-dev libpq-dev

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install Python dependencies in a virtual environment
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

# Runtime stage
FROM python:3.12-alpine

WORKDIR /usr/src/app

# Runtime dependency for psycopg
RUN apk add --no-cache libpq

# Environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN adduser --system --no-create-home nonroot

# Copy UV and virtual environment from build stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY --from=build-stage /usr/src/app/.venv /usr/src/app/.venv

# Fix ownership so nonroot can write to .venv
RUN chown -R nonroot:nobody /usr/src/app/.venv

# Set PATH to use the virtual environment
ENV PATH="/usr/src/app/.venv/bin:$PATH"

# Copy the application code
COPY . .

RUN chown -R nonroot:nobody /usr/src/app

USER nonroot
