# ── Configuration & Variables ───────────────────────────────────────────────

VENV := .venv
SRC  := src
PKG  := img2ascii

# Default target when running just 'make'
.DEFAULT_GOAL := help

# ── Environment ─────────────────────────────────────────────────────────────

.PHONY: install
install: ## Install all dependencies (including dev) via uv
	uv sync --all-groups

.PHONY: install-prod
install-prod: ## Install production dependencies only
	uv sync

# ── Development ─────────────────────────────────────────────────────────────

.PHONY: run
run: ## Run img2ascii CLI (pass IMAGE=<path> [SIZE=<n>] [SAVE=<path>])
	@if [ -z "$(IMAGE)" ]; then echo "Error: IMAGE=<path> is required."; exit 1; fi
	$(eval SIZE ?= 120)
	$(eval SAVE_ARG := $(if $(SAVE),--save $(SAVE),))
	uv run img2ascii --path "$(IMAGE)" --size $(SIZE) $(SAVE_ARG)

# ── Testing ─────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run pytest
	uv run pytest

.PHONY: test-cov
test-cov: ## Run pytest with coverage report
	uv run pytest --cov=$(SRC)/$(PKG) --cov-report=term-missing --cov-report=html

.PHONY: test-watch
test-watch: ## Re-run tests on file change (requires watchexec)
	watchexec -e py -- uv run pytest

# ── Linting & Formatting ────────────────────────────────────────────────────

.PHONY: lint
lint: ## Lint with ruff
	uv run ruff check $(SRC) tests

.PHONY: fmt
fmt: ## Auto-format with ruff
	uv run ruff format $(SRC) tests

.PHONY: fmt-check
fmt-check: ## Check formatting without writing changes
	uv run ruff format --check $(SRC) tests

# ── Build & Publish ─────────────────────────────────────────────────────────

.PHONY: build
build: ## Build the wheel and sdist
	uv build

.PHONY: publish
publish: ## Publish to PyPI (requires PYPI_TOKEN env var)
	@if [ -z "$$PYPI_TOKEN" ]; then echo "Error: PYPI_TOKEN environment variable is not set."; exit 1; fi
	uv publish --token $$PYPI_TOKEN

# ── Cleanup ─────────────────────────────────────────────────────────────────

.PHONY: clean
clean: ## Remove build artifacts and caches
	@rm -rf dist/ .coverage htmlcov/ .pytest_cache/ __pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 
	@find ./ -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
	@find ./ -type f -name "uv.lock" -exec rm -f {} + 2>/dev/null || true
	@find ./ -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find ./ -type d -name "__pycache__" -o -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true

# ── Help / Convenience ──────────────────────────────────────────────────────

.PHONY: help
help: ## Show available tasks
	@echo "Available tasks:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

