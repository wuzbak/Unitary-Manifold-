.PHONY: run install test docker docker-run
install:
	pip install -r requirements.txt
run:
	python run.py
test:
	pytest tests/ -v
docker:
	docker build -t axiom-journalist .
docker-run:
	docker run -p 7870:7870 -v $(PWD)/data:/app/data axiom-journalist
