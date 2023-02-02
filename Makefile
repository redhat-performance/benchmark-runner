.PHONY: golden_files

all: golden_files test_golden_files

golden_files:
	PYTHONPATH=. python3 tests/unittest/benchmark_runner/common/template_operations/generate_golden_files.py

test_golden_files:
	PYTHONPATH=. python3 -m pytest -v tests/unittest/benchmark_runner/common/template_operations/
