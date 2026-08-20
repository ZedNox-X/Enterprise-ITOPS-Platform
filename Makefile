install:
	pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy app

security:
	bandit -r app
	pip-audit

check: lint typecheck test security

up:
	docker compose up --build

down:
	docker compose down -v
