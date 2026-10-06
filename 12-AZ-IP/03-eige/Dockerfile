# AxiomZero EIGE v22 — reproducible test/verifier image
# ======================================================
# Build:   docker build -t axiomzero-eige .
# Test:    docker run --rm axiomzero-eige
# Verify a published bundle (mounted read-only at /bundle):
#          docker run --rm -v "$PWD/bundle:/bundle:ro" axiomzero-eige \
#              python -m eige.verify bundle /bundle
#
# Reproducibility: dependencies are installed with --require-hashes from
# requirements.lock.  For a fully reproducible base, pin PYTHON_IMAGE to a
# digest (python:3.12-slim-bookworm@sha256:...) in your release pipeline.

ARG PYTHON_IMAGE=python:3.12-slim-bookworm
FROM ${PYTHON_IMAGE}

LABEL org.opencontainers.image.title="EIGE" \
      org.opencontainers.image.version="22.0.0" \
      org.opencontainers.image.vendor="AxiomZero Technologies & Consulting, SPC" \
      org.opencontainers.image.description="Election tamper-evidence and audit-support tool (not a voting system)"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    SOURCE_DATE_EPOCH=1767225600 \
    EIGE_MODE=development

WORKDIR /app

COPY requirements.lock ./
RUN pip install --require-hashes --no-deps -r requirements.lock

COPY . ./
RUN useradd --create-home --uid 10001 eige && chown -R eige /app
USER eige

CMD ["python", "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"]
