.PHONY: run install docker docker-run
PRODUCT_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
REPO_ROOT := $(abspath $(PRODUCT_ROOT)/../..)

install:
	pip install -r requirements.txt
run:
	python run.py
docker:
	docker build -t um-sos -f "$(PRODUCT_ROOT)/Dockerfile" "$(REPO_ROOT)"
docker-run:
	docker run -p 127.0.0.1:8000:8000 um-sos
