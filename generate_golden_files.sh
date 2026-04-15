#!/usr/bin/env sh
set -e

if [ ! -d "venv" ]; then
  python3 -m venv venv
  . venv/bin/activate
  pip install -e .
else
  . venv/bin/activate
fi

PYTHONPATH=. python3 \
  tests/unittest/benchmark_runner/common/template_operations/generate_golden_files.py
