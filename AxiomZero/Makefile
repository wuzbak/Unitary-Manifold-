# Makefile — AxiomZero cognitive layer
# Theory: ThomasCory Walker-Pearson | Code: GitHub Copilot (AI)

.PHONY: install install-dev test lint fmt run docker-build clean

PYTHON ?= python3
PIP    ?= $(PYTHON) -m pip

install:
	$(PIP) install -r requirements.txt -e .

install-dev: install
	$(PIP) install pytest pytest-asyncio pytest-cov mypy ruff black

test:
	$(PYTHON) -m pytest tests/ -q --tb=short

test-cov:
	$(PYTHON) -m pytest tests/ --cov=AxiomZero --cov-report=term-missing -q

lint:
	$(PYTHON) -m ruff check AxiomZero/ --fix
	$(PYTHON) -m mypy AxiomZero/ --ignore-missing-imports --no-error-summary

fmt:
	$(PYTHON) -m black AxiomZero/

run:
	$(PYTHON) -m uvicorn AxiomZero.api.server:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t axiomzero:latest -f Dockerfile ..

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov .mypy_cache .ruff_cache
