# Makefile — Unitary Manifold repository
# Theory: ThomasCory Walker-Pearson | Code: GitHub Copilot (AI)

.PHONY: install install-dev test test-core test-pentad test-axiomzero lint fmt \
        build-all docker-up docker-down docs clean run-api run-um-sos

# ── Paths ──────────────────────────────────────────────────────────────────
PYTHON   ?= python3
PIP      ?= $(PYTHON) -m pip
PYTEST   ?= $(PYTHON) -m pytest
UVICORN  ?= $(PYTHON) -m uvicorn

# ── Install ─────────────────────────────────────────────────────────────────
install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e AxiomZero/

install-dev: install
	$(PIP) install -r requirements-dev.txt
	pre-commit install

# ── Test ────────────────────────────────────────────────────────────────────
test:
	$(PYTEST) tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q --tb=short

test-core:
	$(PYTEST) tests/ -q --tb=short

test-pentad:
	$(PYTEST) "5-GOVERNANCE/Unitary Pentad/" -q --tb=short

test-axiomzero:
	$(PYTEST) AxiomZero/tests/ -q --tb=short

test-cov:
	$(PYTEST) tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" \
	    --cov=src --cov=AxiomZero --cov="5-GOVERNANCE/Unitary Pentad" \
	    --cov-report=term-missing --cov-report=html:htmlcov -q

# ── Lint / Format ────────────────────────────────────────────────────────────
lint:
	$(PYTHON) -m ruff check src/ AxiomZero/ "5-GOVERNANCE/Unitary Pentad/" \
	    tests/ 10-UM-SOS/ 12-AZ-IP/ --fix
	$(PYTHON) -m mypy src/ AxiomZero/ --ignore-missing-imports --no-error-summary

fmt:
	$(PYTHON) -m black src/ AxiomZero/ "5-GOVERNANCE/Unitary Pentad/" \
	    tests/ 10-UM-SOS/ 12-AZ-IP/

# ── Build ────────────────────────────────────────────────────────────────────
build-all: build-umos build-azip build-kernel

build-umos:
	$(PYTHON) 10-UM-SOS/scripts/build_registry.py --validate
	$(PYTHON) 10-UM-SOS/scripts/build_graph.py

build-azip:
	@echo "Building 12-AZ-IP packages…"
	@for dir in 12-AZ-IP/apps/*/; do \
	    [ -f "$$dir/pyproject.toml" ] && $(PIP) install -e "$$dir" -q || true; \
	done

build-kernel:
	@if command -v cargo >/dev/null 2>&1; then \
	    cd 11-AZ-OS/ax-kernel && cargo build --release; \
	else \
	    echo "cargo not found — skipping kernel build"; \
	fi

# ── Docker ───────────────────────────────────────────────────────────────────
docker-up:
	docker compose -f 9-INFRASTRUCTURE/monitoring/docker-compose.yml up -d
	docker compose -f AxiomZero/docker-compose.yml up -d

docker-down:
	docker compose -f 9-INFRASTRUCTURE/monitoring/docker-compose.yml down
	docker compose -f AxiomZero/docker-compose.yml down

docker-build:
	docker build -t axiomzero:latest -f AxiomZero/Dockerfile .

# ── Run ──────────────────────────────────────────────────────────────────────
run-api:
	$(UVICORN) AxiomZero.api.server:app --host 0.0.0.0 --port 8000 --reload

run-um-sos:
	$(UVICORN) src.core.um_sos_api:app --host 0.0.0.0 --port 8001 --reload

# ── Docs ─────────────────────────────────────────────────────────────────────
docs:
	$(PYTHON) -m mkdocs build --clean

docs-serve:
	$(PYTHON) -m mkdocs serve

# ── Clean ────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage .mypy_cache .ruff_cache dist build
