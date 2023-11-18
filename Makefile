COMPOSE=docker compose
FEED=$(COMPOSE) run --rm runfeed


runfeed:
	$(FEED) bash -c 'runfeed'