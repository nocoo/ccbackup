#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Running pre-commit checks..."

echo "→ ruff check"
ruff check .

echo "→ ruff format --check"
ruff format --check .

echo "✅ Pre-commit checks passed"
