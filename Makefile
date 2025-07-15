# Project Metadata
PROJECT_NAME := fastapi_boilerplate
ENV_FILE := ".env"
PORT := $(shell grep ^PORT= $(ENV_FILE) | cut -d '=' -f2)

# Commands
PYTHON := uv run python
UVICORN := $(PYTHON) main.py
ISORT := uv run isort .
BLACK := uv run black .
RUFF := uv run ruff .
MYPY := uv run mypy .
PRECOMMIT := uv run pre-commit

# Default
.DEFAULT_GOAL := help

## ----------- Local Development -----------

.PHONY: run
run: ## Run FastAPI app with reload (Dev)
	$(UVICORN) --reload --env-file $(ENV_FILE)

.PHONY: start
start: ## Run FastAPI app for production
	$(UVICORN) --env-file $(ENV_FILE)

.PHONY: shell
shell: ## Open Python shell in uv env
	$(PYTHON)

## ----------- Linting & Formatting -----------

.PHONY: format
format: ## Format code with black and isort
	$(ISORT)
	$(BLACK)

.PHONY: check
check: ## Run pre-commit on all files
	$(PRECOMMIT) run --all-files

.PHONY: install-hooks
install-hooks: ## Install pre-commit hooks
	$(PRECOMMIT) install

## ----------- Testing -----------

.PHONY: test
test: ## Run tests with coverage
	uv run pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

.PHONY: test-fast
test-fast: ## Run tests without coverage (faster)
	uv run pytest tests/ -v

## ----------- Utilities -----------

.PHONY: clean
clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -f .coverage
	rm -f bandit-report.json
	rm -f safety-report.json

.PHONY: help
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync --dev

lint: ## Run linting checks
	uv run ruff check . --fix
	uv run ruff format .

lint-fix: ## Fix linting issues
	uv run ruff check . --fix
	uv run ruff format .

type-check: ## Run type checking
	$(PYTHON) -m mypy app/ --ignore-missing-imports

security-check: ## Run security checks
	uv run bandit -r app/ -f json -o bandit-report.json || true
	uv run safety check --json --output safety-report.json || true

build: ## Build the package
	uv run python -m build

ci: ## Run all CI checks (lint, type-check, test, security)
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	$(MAKE) security-check
	$(MAKE) build

pre-commit: ## Install pre-commit hooks
	uv run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	uv run pre-commit run --all-files

.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -t fastapi-genai-boilerplate:latest .

docker-test: ## Test Docker image
	docker run --rm -d --name test-container -p 8002:8002 fastapi-genai-boilerplate:latest
	sleep 10
	curl -f http://localhost:8002/health || exit 1
	docker stop test-container

docker-clean: ## Clean Docker containers and images
	docker stop test-container 2>/dev/null || true
	docker rm test-container 2>/dev/null || true
	docker rmi fastapi-genai-boilerplate:latest 2>/dev/null || true
	docker rmi fastapi-genai-boilerplate:test 2>/dev/null || true

dev: ## Start development server
	RATE_LIMIT_BACKEND=redis python main.py

dev-frontend: ## Start frontend development server
	cd frontend && npm start

dev-full: ## Start both backend and frontend (requires tmux)
	tmux new-session -d -s dev 'make dev'
	tmux split-window -h 'make dev-frontend'
	tmux attach-session -t dev

stop-dev: ## Stop development servers
	pkill -f "python main.py" || true
	pkill -f "npm start" || true
	tmux kill-session -t dev 2>/dev/null || true
