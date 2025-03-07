#!/bin/bash
echo "Running Black..."
black /app/donordash

echo "Running isort..."
isort /app/donordash

echo "Running flake8..."
flake8 /app/donordash
