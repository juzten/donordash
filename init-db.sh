#!/bin/bash
set -e

# Wait for postgres to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U $POSTGRES_USER -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing database commands"

# Run database initialization commands
echo "Creating database..."
./manage.py create_db

echo "Running database migrations..."
./manage.py db upgrade

# Start the Flask application
exec "$@"
