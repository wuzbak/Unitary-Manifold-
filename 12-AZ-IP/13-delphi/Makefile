.PHONY: run install test docker docker-run seed
install:
	pip install -r requirements.txt
seed:
	python -c "from app.db.seed import seed; seed()"
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
test:
	pytest tests/ -v
docker:
	docker build -t delphi-oracle .
docker-run:
	docker run -p 8080:8080 -v $(PWD)/data:/app/data delphi-oracle
