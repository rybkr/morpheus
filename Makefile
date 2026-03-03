.DEFAULT_GOAL := help

PYTHON ?= python3

## Show available make targets
help:
	@awk 'BEGIN {FS = ":.*$$"} /^## / {desc = substr($$0, 4); next} /^[a-zA-Z0-9_.-]+:/ {if (desc) {printf "%-12s %s\n", $$1, desc; desc = ""}}' $(MAKEFILE_LIST)

## Remove Python/build artifacts from the working tree
clean:
	rm -rf build dist .pytest_cache .mypy_cache .ruff_cache .tox .nox htmlcov .eggs
	rm -f .coverage .coverage.*
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '*.egg-info' -prune -exec rm -rf {} +

## Build source and wheel distributions into dist/
build: clean
	$(PYTHON) -m pip install --upgrade build
	$(PYTHON) -m build

## Validate built distributions (requires dist/)
check:
	$(PYTHON) -m pip install --upgrade twine
	$(PYTHON) -m twine check dist/*

## Show CLI version
version:
	$(PYTHON) -m morpheus.cli --version

## List bundled skills via the CLI
list:
	$(PYTHON) -m morpheus.cli list

.PHONY: help clean build check version list
