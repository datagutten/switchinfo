#!/usr/bin/env sh

# Setup git for config backup
git config --global --add safe.directory "${BACKUP_PATH}"
git config --global user.email "config@backup.local"
git config --global user.name "Config backup"

python3 manage.py collectstatic --noinput
gunicorn