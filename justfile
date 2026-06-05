# Justfile for cee-simulator-backend

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
    sudo docker compose up --build

# ==============================================
# GIT
# ==============================================

# Pull latest changes from the main branch
pull_main:
    git checkout main
    git pull origin main
