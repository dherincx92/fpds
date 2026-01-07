default:
  just --list

venv: ## defaults to creating virtual environment in current directory under .venv
	@if [ -d .venv ]; then \
		echo ".venv already exists. Skipping creation."; \
	else \
		uv venv; \
	fi

install: venv ## updates uv.lock if needed and manually syncs all deps + extras
	uv lock
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
	uv run mypy src/

test: venv install ## Run unit tests with coverage
	uv run -m pytest

local-test:  ## Runs unit tests
	uv run -m pytest --cov=src/ --cov-report term-missing tests/

package: ## builds project + artifacts in dist/ directory
	uv build

publish: package ## publishes package to pypi
	uv publish

scrape: venv install
	uv run python src/fpds/scripts/scraper.py