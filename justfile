# Justfile for crm_epic_events

# Windows shell fix
set shell := ["cmd", "/c"]

# List all available commands
default:
    @just --list


# ==============================================
# CODE QUALITY
# ==============================================

# Automatically fix linting errors
lint:
    uv run ruff check --fix .

# Format the code
format:
    uv run ruff format .

# Run linter and formatter in a single command
check: lint format

# ==============================================
# GIT
# ==============================================

# Run all the tests with coverage included
test:
     just exec pytest .

# Run the tests for a specific file
test-file *args='':
    just exec pytest tests/{{args}}

# ==============================================
# DOCKER
# ==============================================

# Build and start Docker containers
up:
    docker compose -f docker/compose.local.yml up --build -d

# Execute a command in a container
exec *args='':
    docker compose -f docker/compose.local.yml exec crm-app uv run {{args}}

# Stop and remove containers
down:
    docker compose -f docker/compose.local.yml down

# Stop containers and remove all associated volumes
clean:
    docker compose -f docker/compose.local.yml down --volumes

# Remove the crm-app Docker image
clean-image:
    docker rmi crm-epic-events-crm-app

# Remove only the venv volume (forces .venv rebuild on next up)
clean-venv-volume:
    docker volume rm crm-epic-events_crm-app-venv

# Drop and recreate the database
db-drop:
    just exec crm-db psql -U docker_crm_db_user -c "DROP DATABASE IF EXISTS crm_db;" postgres
    just exec crm-db psql -U docker_crm_db_user -c "CREATE DATABASE crm_db;" postgres


# ==============================================
# DATABASE MIGRATIONS
# ==============================================

# Generate a new migration (usage: just migrate "migration message")
migrate msg="":
    just exec alembic revision --autogenerate -m "{{msg}}"

# Apply all pending migrations
db-upgrade:
    just exec alembic upgrade head

# Rollback the last migration
db-downgrade:
    just exec alembic downgrade -1

# Show current migration status
db-status:
    just exec alembic current

# Show migration history
db-history:
    just exec alembic history --verbose


# ==============================================
# GIT
# ==============================================

# Pull latest changes from the main branch
pull_main:
    git checkout main
    git pull origin main
