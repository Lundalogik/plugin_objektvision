.PHONY: help
help:
	@# Print help text
	@./make-help.py $(MAKEFILE_LIST)

.PHONY: build
build:
	@# Build the docker image for plugin_objektvision
	docker build --pull -t plugin_objektvision .

.PHONY: test
test: build
	@# Run unit tests for plugin_objektvision
	docker run plugin_objektvision python3 manage.py test

.PHONY: build-appserver
build-appserver:
	docker build --pull -t plugin_objektvision:latest . -f appserver.Dockerfile

.PHONY: publish-appserver
publish-appserver:
	@export VERSION=`git describe --abbrev=0 --tags 2> /dev/null || echo v0.0.0` \
	&& docker pull $$DOCKER_IMAGE:$$VERSION > /dev/null 2>&1 \
		|| (docker tag plugin_objektvision:latest $$DOCKER_IMAGE:$$VERSION \
			&& docker tag $$DOCKER_IMAGE:$$VERSION $$DOCKER_IMAGE:latest \
			&& docker push  $$DOCKER_IMAGE:latest \
			&& docker push  $$DOCKER_IMAGE:$$VERSION  \
			&& echo "Published $$DOCKER_IMAGE:$$VERSION" \
		)

.PHONY: publish
publish: test
	@# Upload plugin_objektvision to our PyPi server
	@docker run plugin_objektvision python3 manage.py upload --username $(DEVPI_USERNAME) --password $(DEVPI_PASSWORD) --index https://pypi.lundalogik.com:3443/lime/develop/+simple/


.PHONY: ptw
ptw:
	@# Start watching file system for changes and re-run tests when a change is detected.
	docker-compose run app ptw
