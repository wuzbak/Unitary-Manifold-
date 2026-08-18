.PHONY: run install test docker docker-run
install:
	pip install -r requirements.txt
run:
	python run.py
test:
	pytest tests/ -v
docker:
	docker build -t omegaholon .
docker-run:
	docker run -p 7871:7871 -v $(PWD)/data:/app/data omegaholon
