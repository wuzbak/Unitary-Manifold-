.PHONY: run install test docker docker-run
install:
	pip install -r requirements.txt
run:
	python -m lithic.app.main
test:
	pytest tests/ -v
docker:
	docker build -t lithos-os .
docker-run:
	docker run -p 7861:7861 -v $(PWD)/data:/app/data lithos-os
