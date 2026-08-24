# Multi-stage build: dependencies are resolved once in the builder and the
# runtime image carries no build toolchain, no Pipfile and no pipenv.

FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=5

RUN pip install pipenv

# The venv must be built at the path it will live at in the runtime image:
# console scripts bake an absolute interpreter path into their shebang.
WORKDIR /app
COPY Pipfile Pipfile.lock ./

# --deploy fails the build if Pipfile.lock is out of date with Pipfile, so an
# image can never be produced from unlocked dependencies.
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --python /usr/local/bin/python


FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app" \
    PATH="/app/.venv/bin:$PATH"

# Run as an unprivileged user.
RUN groupadd --system app && useradd --system --gid app --home /app app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --chown=app:app alembic.ini pyproject.toml ./
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app app ./app
COPY --chown=app:app scripts ./scripts

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
