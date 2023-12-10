COMPOSE=docker compose
FEED=$(COMPOSE) run --rm runfeed


runfeed:
	$(FEED) bash -c 'runfeed'

build:
	$(COMPOSE) build
start:
	$(COMPOSE) up -d
stop:
	$(COMPOSE) down
logs:
	$(COMPOSE) logs --follow --tail 1000
local-setup:
	${COMPOSE} up db redis