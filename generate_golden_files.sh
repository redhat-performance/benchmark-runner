#!/usr/bin/env sh

python3 -m venv venv
. .venv/bin/activate
PYTHONPATH=. python3 tests/unittest/benchmark_runner/common/template_operations/generate_golden_files.py
