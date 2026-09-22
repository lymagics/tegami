.DEFAULT_GOAL := help
.PHONY: help sync unit black flake8 ruff lint

help:
	@echo "Tegami development commands"
	@echo ""
	@echo "  make sync      Install project and dev dependencies with uv"
	@echo "  make unit      Run unit tests with coverage"
	@echo "  make black     Check formatting with black"
	@echo "  make flake8    Lint with flake8"
	@echo "  make ruff      Lint with ruff"
	@echo "  make lint      Run black, flake8 and ruff"
	@echo "  make help      Show this help"

sync:
	uv sync

unit:
	uv run pytest

black:
	uv run black --check tegami tests

flake8:
	uv run flake8 tegami tests

ruff:
	uv run ruff check tegami tests

lint: black flake8 ruff
