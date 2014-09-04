.PHONY: build

help:
	@echo "build - Build docker container"
	@echo "run - Run builder inside a Docker container (in production mode)"
	@echo "run-local - Run builder locally (for development purposes) inside a Docker container"

build:
	docker build -t="beardo/beardo-build" .

store-image: build
	-rm build/beardo-build.tar.gz
	docker save beardo/beardo-build > build/beardo-build.tar
	gzip build/beardo-build.tar

deploy: store-image
	docker run -t -i -v $(CURDIR)/assets/:/assets/ -v $(CURDIR)/build/:/build/ -v $(CURDIR)/scripts/:/scripts/ -v $(CURDIR)/secrets/:/secrets/ beardo/beardo-build python /scripts/validate.py
	docker run -t -i -v $(CURDIR)/assets/:/assets/ -v $(CURDIR)/build/:/build/ -v $(CURDIR)/scripts/:/scripts/ -v $(CURDIR)/secrets/:/secrets/ beardo/beardo-build fab -f /scripts/fabfile.py with_config deploy
	rm build/beardo-build.tar.gz

remote-status: build
	docker run -t -i -v $(CURDIR)/assets/:/assets/ -v $(CURDIR)/build/:/build/ -v $(CURDIR)/scripts/:/scripts/ -v $(CURDIR)/secrets/:/secrets/ beardo/beardo-build fab -f /scripts/fabfile.py with_config service_status

run: build
	docker run --privileged -t -i beardo/beardo-build
