#!/usr/bin/env bash
set -euo pipefail

echo "🔍 Running pre-push checks..."

echo "→ ruff check"
ruff check .

echo "→ ruff format --check"
ruff format --check .

echo "→ pytest"
python3 -m pytest tests/ -v

echo "→ gitleaks"
if command -v gitleaks &>/dev/null; then
    gitleaks detect --source . --no-banner
else
    echo "⚠️  gitleaks not installed, skipping"
fi

echo "✅ Pre-push checks passed"
