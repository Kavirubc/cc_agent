#!/bin/bash

# Set the project directory
PROJECT_DIR=$(dirname "$0")
cd "$PROJECT_DIR"

# Create a virtual environment
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the FastAPI application
echo "Starting the FastAPI application..."
python src/cc_agent/api.py