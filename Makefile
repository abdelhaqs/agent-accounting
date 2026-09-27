.PHONY: help test lint format data-check clean

help:
	@echo "Agent Accounting Pipeline — Developer CLI"
	@echo "========================================="
	@echo "make test        : Run full unit test suite and data quality contracts"
	@echo "make lint        : Lint codebase with flake8"
	@echo "make format      : Format codebase using black"
	@echo "make data-check  : Validate data quality assertions"
	@echo "make clean       : Remove Python bytecode and temporary caches"

test:
	pytest tests/ -v

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=local_tests,venv,.venv,archive_downloads,Archive
	flake8 . --count --exit-zero --max-complexity=15 --max-line-length=130 --statistics --exclude=local_tests,venv,.venv,archive_downloads,Archive

format:
	black --line-length 130 .

data-check:
	pytest tests/test_data_quality.py -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
