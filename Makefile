.PHONY: black clean help install isort lint mypy formatters test local-test venv build-flow register-flow
.DEFAULT_GOAL := help

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

install: ## Install the package dev to the active Python's site-packages
	if [ -z ${VIRTUAL_ENV} ]; then \
	  echo "\nattempting to activate venv\n" \
	  && . ./venv/bin/activate \
	  && pip3 install --upgrade pip \
	  && pip3 install -r requirements.txt --no-cache-dir \
	  && pip3 install -e '.[dev, tests]'; \
	else  \
	  echo "\nvirtual environment detected\n" \
	  && pip3 install --upgrade pip \
	  && pip3 install -r requirements.txt --no-cache-dir \
	  && pip3 install -e '.[dev, tests]';\
	fi

clean: ## Remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

black: ## Format with black
	black src tests setup.py

isort: ## Format and sort imports
	isort src

lint: ## Check style with flake8
	flake8 src tests

mypy: ## Typechecking with mypy
	mypy src tests

formatters: black isort lint mypy

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
	pytest --cov=src/ --cov-report term-missing src/fpds/tests/

venv: ## Check if operating in a virtual environment, create if not detected.
	if [ ! -z ${VIRTUAL_ENV} ]; then echo "\nvirtual environment detected\n"; else python3.8 -m venv venv && . ./venv/bin/activate; fi
