#!/usr/bin/env bash
# Create GitHub repo medicaid-exclusion-list and push (run once after gh auth login).
set -euo pipefail

REPO_NAME="medicaid-exclusion-list"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

if ! command -v gh &>/dev/null; then
  echo "GitHub CLI (gh) not found."
  echo "Install: brew install gh"
  echo "Or download: https://cli.github.com/"
  exit 1
fi

if ! gh auth status &>/dev/null; then
  echo "Log in to GitHub first:"
  gh auth login
fi

if git remote get-url origin &>/dev/null; then
  echo "Remote origin already set. Pushing..."
  git push -u origin main
else
  echo "Creating public repo: $REPO_NAME"
  gh repo create "$REPO_NAME" \
    --public \
    --source=. \
    --remote=origin \
    --push \
    --description "39-state Medicaid exclusion list + federal LEIE ETL, PostgreSQL, Django web search"
fi

echo ""
echo "Done. View at: https://github.com/$(gh api user -q .login)/$REPO_NAME"
