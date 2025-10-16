#!/bin/env bash

# Database Initialization Script
# This script prepares the SQLite database by running data cleaning and setup

set -e  # exit on any error

echo "Starting database initialization..."

# cleaning our dataset
echo "Running data cleaning..."
python data/cleaning.py

# database setup script
echo "Setting up database..."
python db/db_setup.py

echo "Database initialization completed successfully!"

exec uvicorn main:app --host 0.0.0.0 --port 8000