#!/usr/bin/env bash
set -euo pipefail

pattern='g''hp_[A-Za-z0-9]+|github_''pat_[A-Za-z0-9_]+|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY'
pathspec=(-- . ':!.env.example' ':!scripts/scan_secrets.sh')

if git log --all --format=%H -- .env | grep --quiet .; then
  echo "error: .env exists in Git history" >&2
  exit 1
fi

if git grep --cached --quiet --ignore-case --extended-regexp "$pattern" "${pathspec[@]}"; then
  echo "error: secret-like pattern found in index" >&2
  exit 1
fi

while read -r commit; do
  if git grep --quiet --ignore-case --extended-regexp "$pattern" "$commit" "${pathspec[@]}"; then
    echo "error: secret-like pattern found in Git history" >&2
    exit 1
  fi
done < <(git rev-list --all)

echo "Secret pattern and .env history scan passed"
