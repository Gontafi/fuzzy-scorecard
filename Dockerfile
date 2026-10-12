# Container image for the fuzzyscore package.
# Build:  docker build -t fuzzyscore .
# Run:    docker run --rm fuzzyscore demo --n 5000
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install the package first so the dependency layer is cached between builds.
COPY pyproject.toml README.md LICENSE ./
COPY fuzzyscore ./fuzzyscore
RUN pip install .

# Run as an unprivileged user.
RUN useradd --create-home --uid 1000 app && chown -R app:app /app
USER app

ENTRYPOINT ["fuzzyscore"]
CMD ["demo", "--n", "5000"]

# Test stage: the Jenkins pipeline builds this target to run the test suite
# inside the same image that is shipped.
FROM base AS test
USER root
COPY tests ./tests
RUN pip install pytest pytest-cov ruff && mkdir -p /app/reports && chown -R app:app /app
USER app
ENV COVERAGE_FILE=/tmp/.coverage PYTHONPATH=/app
ENTRYPOINT ["pytest"]
CMD ["-q"]
