SHELL := /bin/bash

.PHONY: build up down restart logs status health test reset

build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d --build

logs:
	docker compose logs -f --tail=100

status:
	./scripts/status.sh

health:
	./scripts/healthcheck.sh

test:
	./scripts/test-all.sh

reset:
	./scripts/reset-all.sh
