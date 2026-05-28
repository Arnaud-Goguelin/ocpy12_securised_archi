#!/bin/sh

set -e

echo "Starting CRM CLI..."
exec python -m crm_epic_events "$@"
