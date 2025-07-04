.PHONY: help install install-dev run test lint format docker-build docker-run clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements-dev.txt
	pre-commit install

run: ## Run the development server
	python -m uvicorn src.tickethub.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	python -m pytest tests/ -v --cov=src/tickethub --cov-report=html --cov-report=term

test-unit: ## Run unit tests only
	python -m pytest tests/test_models.py tests/test_services.py -v

test-integration: ## Run integration tests only
	python -m pytest tests/test_main.py -v

lint: ## Run linting
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/

check: ## Run all checks (lint + test)
	make lint
	make test

docker-build: ## Build Docker image
	docker build -t tickethub:latest .

docker-run: ## Run with Docker Compose
	docker-compose up --build

docker-stop: ## Stop Docker Compose
	docker-compose down

docker-clean: ## Clean Docker containers and images
	docker-compose down -v
	docker rmi tickethub:latest || true

clean: ## Clean Python cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

dev-setup: install-dev ## Complete development setup
	@echo "Development environment ready!"
	@echo "Run 'make run' to start the server"
