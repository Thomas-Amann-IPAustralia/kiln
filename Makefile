# One command per habit. `make check` is what CI runs.
.PHONY: setup check fix doctor

setup:
	uv sync
	uv run pre-commit install

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run pyright
	uv run pytest
	uv run kiln records check

fix:
	uv run ruff check --fix .
	uv run ruff format .

doctor:
	uv run kiln doctor
