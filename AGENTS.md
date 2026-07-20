# Repository Guide

## Structure

- `config/`: Django settings, root URLs, ASGI/WSGI entry points
- `users/`: authentication, profiles, account status
- `products/`: product CRUD, images, public search
- `wallets/`: point wallets, transfers, immutable ledger
- `moderation/`: reports, sanctions, administrator audit records
- `adjustments/`: audited administrator point adjustments
- `chat/`: global/direct conversations, persisted messages, WebSockets
- `security_controls/`: privacy-preserving login throttling
- `templates/`: server-rendered Bootstrap templates
- `docs/`: requirements, design, security, testing, progress, ADRs

## Commands

- Setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt`
- Run: `.venv/bin/python manage.py migrate && .venv/bin/python manage.py runserver`
- Test: `.venv/bin/pytest`
- Lint: `.venv/bin/ruff check .`
- Format check: `.venv/bin/ruff format --check .`
- Security: `.venv/bin/bandit -c pyproject.toml -r config users products wallets moderation adjustments chat security_controls && .venv/bin/pip-audit -r requirements.txt`
- Secret history: `bash scripts/scan_secrets.sh`
- E2E: `bash scripts/run_e2e.sh` (PostgreSQL, Redis, Playwright Chromium and E2E environment variables required)

## Rules

- Keep authorization, ownership, participant, account-status, and administrator checks on the server.
- Use Django ORM; never interpolate user input into SQL.
- Validate uploaded size, extension, MIME type, and image contents.
- Keep secrets in environment variables; never commit `.env`.
- Use transactions and row locks for balance changes and concurrent rate-limit decisions.
- Add normal, failure, unauthenticated, and forbidden tests with each feature.
- Do not force-push, rewrite shared history, commit credentials, or hard-delete audit/ledger records.

## Definition of Done

Implementation, tests, requirement traceability, security notes, progress notes, and a clean Git diff are all required.
