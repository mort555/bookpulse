
.PHONY: up down test lint migrate seed

up:
	docker compose -f compose.yml up --build -d

down:
	docker compose -f compose.yml down

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy app
	uv run lint-imports

migrate:
	uv run alembic upgrade head

seed:
	uv run python -m app.cli seed
