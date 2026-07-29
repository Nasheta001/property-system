# syntax=docker/dockerfile:1

# --------------------------------------------------------------------------
# Base: shared system dependencies for every stage
# --------------------------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --------------------------------------------------------------------------
# Development: editable install, dev tooling, code mounted as a volume
# --------------------------------------------------------------------------
FROM base AS development

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip install -r requirements/development.txt

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# --------------------------------------------------------------------------
# Build: compiles wheels for production, keeping the final image slim
# --------------------------------------------------------------------------
FROM base AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ requirements/
RUN pip wheel --wheel-dir /wheels -r requirements/production.txt

# --------------------------------------------------------------------------
# Production: minimal runtime image, runs as a non-root user under gunicorn
# --------------------------------------------------------------------------
FROM base AS production

RUN groupadd --system app && useradd --system --gid app --no-create-home app

COPY --from=build /wheels /wheels
COPY requirements/ requirements/
RUN pip install --no-index --find-links=/wheels -r requirements/production.txt \
    && rm -rf /wheels

COPY . .
RUN chmod +x entrypoint.sh && chown -R app:app /app

USER app

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
