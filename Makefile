.PHONY: help build up down restart logs clean test migrate shell

help:
	@echo "Bankrot Pro - Makefile commands"
	@echo ""
	@echo "  make build      - Build Docker containers"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs (all services)"
	@echo "  make logs-api   - View API logs"
	@echo "  make logs-bot   - View bot logs"
	@echo "  make logs-web   - View web logs"
	@echo "  make clean      - Remove containers and volumes"
	@echo "  make test       - Run tests"
	@echo "  make migrate    - Run database migrations"
	@echo "  make shell-api  - Open shell in API container"
	@echo "  make shell-bot  - Open shell in bot container"
	@echo "  make backup-db  - Backup database"

build:
	docker compose build

up:
	docker compose up -d
	@echo "Services started!"
	@echo "Web UI: http://localhost:8501"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-bot:
	docker compose logs -f bot

logs-web:
	docker compose logs -f web

clean:
	docker compose down -v
	@echo "All containers and volumes removed"

test:
	docker compose exec api pytest tests/ -v

migrate:
	docker compose exec api alembic upgrade head
	@echo "Migrations applied"

migrate-create:
	@read -p "Enter migration message: " msg; \
	docker compose exec api alembic revision --autogenerate -m "$$msg"

shell-api:
	docker compose exec api bash

shell-bot:
	docker compose exec bot bash

shell-db:
	docker compose exec postgres psql -U bankrot bankrot

backup-db:
	@echo "Creating database backup..."
	docker compose exec postgres pg_dump -U bankrot bankrot > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup saved to backup_$$(date +%Y%m%d_%H%M%S).sql"

ps:
	docker compose ps

stats:
	docker stats
