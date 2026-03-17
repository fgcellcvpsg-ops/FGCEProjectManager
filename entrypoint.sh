#!/usr/bin/env bash
# exit on error
set -o errexit

# Run migrations
echo "Running migrations..."
flask db upgrade

# Seed admin
echo "Seeding admin..."
python seed_admin.py

# Start app
echo "Starting Gunicorn..."
exec gunicorn run:app