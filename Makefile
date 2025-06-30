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
	rm -fr .pytest_cache
	rm -fr .mypy_cache

formatters: venv ## formats using ruff
	uv tool run ruff format

mypy: ## Typechecking with mypy
	mypy src


test: venv install ## Run unit tests with coverage
	if [ -z ${VIRTUAL_ENV} ]; then \
	  echo "\nattempting to activate virtual environment\n" \
	  && . ./venv/bin/activate \
	  && pytest --cov=src/ --cov-report term-missing tests/ \
	  && coverage report --fail-under=70 \
	  && rm -rf .coverage; \
	else \
	  echo "\nvirtual environment detected\n" \
	  && pytest --cov=src/ --cov-report term-missing tests/ \
	  && coverage report --fail-under=70 \
	  && rm -rf .coverage; \
	fi

local-test:  ## Runs unit tests
	pytest --cov=src/ --cov-report term-missing tests/


package:
	@ pip install -U pip
	@ pip install .[packaging]
	@ python -m build --sdist --wheel --outdir dist/ .

publish: venv login
	twine upload --verbose dist/*