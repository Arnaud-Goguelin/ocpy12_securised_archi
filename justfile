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
# DOCKER
# ==============================================

# Build and start Docker containers
up:
    docker compose -f docker/compose.local.yml up -d

# Execute a command in a container
exec *args='':
    docker compose -f docker/compose.local.yml exec crm-app $@

# ==============================================
# GIT
# ==============================================

# Pull latest changes from the main branch
pull_main:
    git checkout main
    git pull origin main
