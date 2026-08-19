.PHONY: run install docker docker-run
install:
	pip install -r requirements.txt
run:
	python backend/app.py
docker:
	docker build -t um-sos .
docker-run:
	docker run -p 8000:8000 um-sos
