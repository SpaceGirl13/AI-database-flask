#!/bin/bash
set -e

echo "Running database migrations..."
python migrate_db.py

echo "Starting Flask application with Gunicorn..."
exec gunicorn main:app --workers=5 --threads=2 --bind=0.0.0.0:8402 --timeout=30 --access-logfile -
