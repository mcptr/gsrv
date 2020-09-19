DOCKER_IMG_NAME 	?=
DOCKER_OPTIONS		?=


docker-assert:
	test $(DOCKER_IMG_NAME) || (echo "DOCKER_IMG_NAME not set" && exit 1)
	stat Dockerfile > /dev/null || (echo "No Dockerfile" && exit 1)

docker-setup: docker-build

docker-build: docker-assert
	docker build -t $(DOCKER_IMG_NAME) $(DOCKER_OPTIONS) .

docker-build-nc: docker-assert
	docker build --no-cache -t $(DOCKER_IMG_NAME) $(DOCKER_OPTIONS) .
