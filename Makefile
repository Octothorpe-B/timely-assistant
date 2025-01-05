# Variables
PIP := pip3
PYTHON := python3
PYTEST := pytest
PYLINT := pylint
MYPY := mypy
BANDIT := bandit

# Default target.
.PHONY: all
all: install test

# Install dependencies
.PHONY: install
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Clean up installed packages.
.PHONY: clean
clean:
	$(PIP) uninstall -y -r requirements.txt

.PHONY: test
test:
	$(PYTHONPATH=src PYTEST -v)


# Run the application.
.PHONY: run
run:
	$(python) src/main.py