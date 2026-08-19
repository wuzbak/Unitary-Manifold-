.PHONY: test docker docker-test install
install:
	pip install -r requirements.txt
test:
	pytest tests/ -v
docker:
	docker build -t axiomzero-eige .
docker-test:
	docker run --rm axiomzero-eige
