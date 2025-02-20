#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run pre-commit hooks on all files
pre-commit run --all-files

echo "Setup complete! Pre-commit hooks are now installed and configured." 