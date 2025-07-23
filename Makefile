.PHONY: help install test lint format clean run dev setup

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	venv/bin/pip install -r requirements.txt

install-dev: ## Install development dependencies
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -e .[dev]

setup: ## Initial setup (install dependencies, setup pre-commit)
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -e .[dev]
	venv/bin/pre-commit install

test: ## Run tests
	venv/bin/pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	venv/bin/pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing -f

lint: ## Run linting
	venv/bin/flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	venv/bin/flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

format: ## Format code with black
	venv/bin/black .

type-check: ## Run type checking
	venv/bin/mypy . --ignore-missing-imports

check: ## Run all checks (lint, format, type-check, test)
	venv/bin/flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	venv/bin/black . --check
	venv/bin/mypy . --ignore-missing-imports
	venv/bin/pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	find . -name ".coverage" -delete
	find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true

run: ## Run the application (production)
	./start_app.sh production

dev: ## Run in development mode
	./start_app.sh development

start: ## Start the application (alias for dev)
	./start_app.sh development

logs: ## Show application logs
	tail -f data/logs/leadfinder.log

logs-clear: ## Clear application logs
	> data/logs/leadfinder.log

db-reset: ## Reset database (WARNING: This will delete all data)
	rm -f data/*.db
	venv/bin/python -c "from models.database import DatabaseConnection; db = DatabaseConnection(); db.create_tables()"

security: ## Run security checks
	venv/bin/bandit -r . -f json -o bandit-report.json
	venv/bin/safety check --json --output safety-report.json

pre-commit: ## Run pre-commit hooks
	venv/bin/pre-commit run --all-files

update-deps: ## Update dependencies
	venv/bin/pip install --upgrade -r requirements.txt
	venv/bin/pip install --upgrade -e .[dev] 