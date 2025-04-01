#!/bin/bash

# Script to install test dependencies and run tests

# Set error handling
set -e

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
  if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
  else
    echo "No virtual environment found. Creating one..."
    uv venv
    source .venv/bin/activate
  fi
fi

# Install dependencies
echo "Installing test dependencies..."
uv pip install -r requirements-dev.txt

# Run the tests using uv run
echo "Running tests..."
uv run -- pytest "$@"

echo "Tests completed!" 