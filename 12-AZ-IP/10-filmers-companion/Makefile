.PHONY: run install test docker docker-run android
install:
	pip install -r requirements.txt
run:
	python -m desktop.app.main
test:
	pytest desktop/tests/ -v
docker:
	docker build -t filmers-companion .
docker-run:
	docker run -p 7864:7864 -v $(PWD)/data:/app/data filmers-companion
android:
	cd android && ./gradlew assembleDebug
