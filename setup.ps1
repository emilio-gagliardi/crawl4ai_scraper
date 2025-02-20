# Install Python dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Install pre-commit hooks
Write-Host "Installing pre-commit hooks..."
pre-commit install

# Run pre-commit hooks on all files
Write-Host "Running pre-commit hooks on all files..."
pre-commit run --all-files

Write-Host "Setup complete! Pre-commit hooks are now installed and configured." 