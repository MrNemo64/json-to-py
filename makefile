.PHONY: test lint format

PYTHON=python3

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests

lint:
	flake8 src/ tests/

format:
	black src/ tests/
