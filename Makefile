.PHONY: install format lint typecheck test check clean

install:
	uv sync --all-groups || python -m pip install -e ".[dev]"

format:
	ruff format .

lint:
	ruff check .

typecheck:
	mypy apps services agents tools plugins

test:
	pytest

check: lint typecheck test

clean:
	python -c "import shutil; [shutil.rmtree(path, ignore_errors=True) for path in ('.pytest_cache', '.mypy_cache', '.ruff_cache', 'htmlcov', 'build', 'dist')]"
