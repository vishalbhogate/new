# load and export .env
ifneq (,$(wildcard ./.env))
include .env
export
endif


## vars
EXECUTOR_IMAGE ?= gitlab-runner-pm-docker-executor
DOCKER_IMAGE_NAME ?= $(PM_BUILD_ACCOUNT_ID).dkr.ecr.ap-southeast-2.amazonaws.com/$(EXECUTOR_IMAGE):latest
BUILD_ID ?= $(shell date +%s)
COMPOSE_RUN_DOCKER=DOCKER_IMAGE_NAME=$(DOCKER_IMAGE_NAME) BUILD_ID=$(BUILD_ID) docker-compose run --rm aws


lint: dotenv
	$(COMPOSE_RUN_DOCKER) make _lint
.PHONY: lint

_lint:
	bash scripts/tf-lint.sh
.PHONY: _lint

# replaces .env with DOTENV if the variable is specified
dotenv:
ifdef DOTENV
	cp -f $(DOTENV) .env
else
	$(MAKE) .env
endif
ifdef CI
	@mkdir -p ~/.docker
	@echo '${DOCKER_AUTH_CONFIG}' > ~/.docker/config.json
	env >> .env
endif

# creates .env with .env.template if it doesn't exist already
.env:
	cp -f .env.template .env



## assume role Make function
_assumeRole:
ifdef AWS_ROLE
		@echo "Assuming into role: $(AWS_ROLE)"
		$(call assumeRole)
endif

ifdef AWS_ROLE
define assumeRole
	$(eval KST = $(shell aws sts assume-role --role-arn $(AWS_ROLE) --duration-seconds $(AWS_ROLE_SESSION_DURATION) --role-session-name cd | jq -rc '.Credentials.AccessKeyId,.Credentials.SecretAccessKey,.Credentials.SessionToken' | awk 1 ORS=' '))
	$(eval export AWS_ACCESS_KEY_ID = $(shell echo $(KST) | cut -d ' ' -f1))
	$(eval export AWS_SECRET_ACCESS_KEY = $(shell echo $(KST) | cut -d ' ' -f2))
	$(eval export AWS_SESSION_TOKEN = $(shell echo $(KST) | cut -d ' ' -f3))
endef
endif
