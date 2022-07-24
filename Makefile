SHELL := bash
DOCKER_CHECK := $(shell command -v docker > /dev/null 2>&1 ; echo $$? )
ifeq ($(DOCKER_CHECK), 0)
BIN := docker
else
BIN := hugo
endif

ifeq ($(BIN), hugo)
BIN_FLAGS := serve -D
else
BIN_FLAGS := container run --rm -it -v "$${PWD}":/app -w /app -p $${HOST_IP:-127.0.0.1}:1313:1313 jb_hugo:latest
endif

dev: deps
	$(BIN) $(BIN_FLAGS)

deps:
	if [ "$(BIN)" == hugo ] ; then \
		hugo version | grep 'extended' >/dev/null || (echo "You don't have the extended version of hugo, please install it" && exit 1); \
	else \
		docker build --rm -f Dockerfile -t jb_hugo:latest . ;\
	fi
