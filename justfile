set shell := ["pwsh", "-NoLogo", "-NoProfile", "-Command"]

default: check

install:
    uv sync --extra dev --extra dlt

test:
    uv run python -c "from pathlib import Path; Path('artifacts').mkdir(exist_ok=True)"
    uv run --extra dev --extra dlt pytest --junitxml=artifacts/junit.xml --cov=dlt_parentsquare --cov-report=term-missing --cov-report=xml:artifacts/coverage.xml

lint:
    uv run --extra dev --extra dlt ruff check .

format:
    uv run --extra dev --extra dlt ruff format --check .

typecheck:
    uv run --extra dev --extra dlt pyrefly check

prek:
    uvx prek run --all-files

check: lint format typecheck test
