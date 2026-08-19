.PHONY: run install test docker docker-run
install:
	pip install -r requirements.txt
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
test:
	pytest tests/ -v
docker:
	docker build -t terra-os .
docker-run:
	docker run -p 8001:8001 --env-file .env terra-os
