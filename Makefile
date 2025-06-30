.PHONY: help venv install clean formatters mypy test local-test package publish
.DEFAULT_GOAL := help

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

venv: ## defaults to creating virtual environment in current directory under .venv
	uv venv

install: venv ## checks if uv.lock is up-to-date and manually syncs all deps + extras
	uv lock --check
	uv sync --extra all

clean: ## Remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .ruff_cache
	rm -fr .pytest_cache
	rm -fr .mypy_cache

formatters: venv ## https://docs.astral.sh/ruff/formatter/#line-breaks
	uv tool run ruff check --select I --fix
	uv tool run ruff format

mypy: ## Typechecking with mypy
	mypy src

test: venv install ## Run unit tests with coverage
	uv run -m pytest

local-test:  ## Runs unit tests
	uv run -m pytest --cov=src/ --cov-report term-missing tests/

package:
	@ pip install -U pip
	@ pip install .[packaging]
	@ python -m build --sdist --wheel --outdir dist/ .

publish: venv login
	twine upload --verbose dist/*