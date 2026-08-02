# AxiomZero EIGE v21.0 — Docker Image
# =====================================
# Builds a self-contained image that runs the full 449-test suite.
# Usage:
#   docker build -t axiomzero-eige .
#   docker run --rm axiomzero-eige
#
# To run an interactive shell instead:
#   docker run --rm -it axiomzero-eige /bin/bash

FROM python:3.12-slim

LABEL maintainer="AxiomZero Technologies & Consulting, SPC"
LABEL version="21.0.0"
LABEL description="EIGE — Election Integrity Governance Engine"

WORKDIR /app

# Copy EIGE package and top-level dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full EIGE directory (src, tests, docs)
COPY . ./EIGE/

# Make the EIGE src package importable
ENV PYTHONPATH=/app

# Default command: run the full test suite
CMD ["python", "-m", "pytest", "EIGE/tests/", "-v", "--tb=short"]
