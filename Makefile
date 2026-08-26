.DEFAULT_GOAL := help
.PHONY: help install dev dev-web dev-api check check-web check-api test test-web test-api e2e seed seed-check db-up db-down db-logs clean

WEB := apps/web
API := apps/api

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies for both applications
	cd $(WEB) && npm ci
	cd $(API) && uv sync --all-extras

dev: ## Run the API and the web app together
	@echo "API  -> http://localhost:8000/docs"
	@echo "Web  -> http://localhost:5173"
	@$(MAKE) -j2 dev-api dev-web

dev-web: ## Run the web app only
	cd $(WEB) && npm run dev

dev-api: ## Run the API only
	cd $(API) && uv run uvicorn portfolio_api.main:app --reload --port 8000

check: check-web check-api ## Lint, typecheck and unit-test both applications

check-web: ## Quality gates for the web app
	cd $(WEB) && npm run lint && npm run typecheck && npm run test

check-api: ## Quality gates for the API
	cd $(API) && uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest

test: test-web test-api ## Run all tests

test-web:
	cd $(WEB) && npm run test:coverage

test-api:
	cd $(API) && uv run pytest --cov

e2e: ## Run the Playwright end-to-end suite
	cd $(WEB) && npm run e2e

seed: ## Load content/ into MongoDB (idempotent)
	cd $(API) && uv run python -m portfolio_api.seed

seed-check: ## Validate content/ without writing to the database
	cd $(API) && uv run python -m portfolio_api.seed --check

db-up: ## Start local MongoDB
	docker compose -f infra/docker-compose.yml up -d

db-down: ## Stop local MongoDB
	docker compose -f infra/docker-compose.yml down

db-logs: ## Tail MongoDB logs
	docker compose -f infra/docker-compose.yml logs -f mongo

clean: ## Remove build artefacts and caches
	rm -rf $(WEB)/dist $(WEB)/coverage $(WEB)/playwright-report $(WEB)/test-results
	rm -rf $(API)/.pytest_cache $(API)/.mypy_cache $(API)/.ruff_cache $(API)/htmlcov
