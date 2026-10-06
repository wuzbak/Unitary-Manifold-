.PHONY: install test verify-demo sbom sbom-check vectors vectors-check docker docker-test
install:
	pip install --require-hashes -r requirements.lock
test:
	python -m pytest tests -q
verify-demo:
	python run_demo.py
sbom:
	python tools/make_sbom.py
sbom-check:
	python tools/make_sbom.py --check
vectors:
	python tools/make_test_vectors.py
vectors-check:
	python tools/make_test_vectors.py --check
docker:
	docker build -t axiomzero-eige .
docker-test:
	docker run --rm axiomzero-eige
