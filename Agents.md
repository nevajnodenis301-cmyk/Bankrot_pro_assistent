# BankrotPro AI Agents Configuration

## Project Overview
Russian bankruptcy case management system (Federal Law 127-FZ)

## Tech Stack
- Backend: FastAPI, PostgreSQL 15, Redis, Alembic
- Frontend: Streamlit  
- Bot: Telegram (aiogram 3.x)
- Docs: python-docx-template (Jinja2)
- Security: JWT auth, AES-256-GCM encryption (25 PII fields)
- Infrastructure: Docker Compose

## Key Directories
- `/api` - FastAPI backend (main.py, auth.py, encryption.py, database.py)
- `/bot` - Telegram bot handlers
- `/web` - Streamlit UI (pages/2_➕_Новое_дело.py - 13-section form)
- `/migrations` - Alembic migrations
- `/templates` - DOCX templates (Jinja2 syntax)

## Current Priorities
1. Verify encryption working (check DB, test decryption)
2. Test Telegram bot integration
3. Validate document generation
4. Deploy to production (193.160.208.85)

## Critical Rules
- Case numbers: `BP-YYYY-NNNN` format
- Template syntax: Jinja2 (`{% if %}`) not Mustache (`{{#if}}`)
- All PII encrypted at rest (passport, INN, SNILS, phones, addresses)
- Russian legal compliance (Federal Law 127-FZ)
- PowerShell environment (Windows)

## Common Commands
```bash
# Database migration
alembic upgrade head

# Docker rebuild
docker-compose up --build

# Check encryption
docker-compose exec db psql -U bankrotpro -d bankrotpro -c "SELECT debtor_passport_series FROM cases WHERE id=1;"
```

## Known Gotchas
- `.get()` with None: use `dict.get("key") or 0`
- Docker rebuild required after pip installs
- Template syntax converted from Mustache to Jinja2

## Team
- Denis (Project Lead) - Final decisions
- Claude (Senior Dev) - Architecture, terminal ops