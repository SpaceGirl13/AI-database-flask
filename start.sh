#!/bin/bash
set -e

echo "Running database migrations..."
python migrate_db.py

echo "Starting Flask application..."
exec python app.py
