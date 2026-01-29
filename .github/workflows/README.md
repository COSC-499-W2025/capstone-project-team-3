# CI/CD Workflows

This directory contains GitHub Actions workflows for automated testing and quality checks.

## Workflows 

### 1. **CI Pipeline** (`ci.yml`)
- **Triggers**: On every PR and push to main/master
- **Purpose**: Runs all tests with pytest and generates coverage reports
- **Why**: Catches bugs before they reach production

### 2. **Docker Build** (`docker.yml`)
- **Triggers**: On every PR and push to main/master
- **Purpose**: Validates that Docker images build successfully
- **Why**: Prevents deployment failures due to Docker issues

### 3. **Security Scan** (`security.yml`)
- **Triggers**: On every PR, push, and weekly schedule
- **Purpose**: Scans dependencies for known vulnerabilities
- **Why**: Keeps the project secure from vulnerable packages

### 4. **Test Coverage** (`coverage.yml`)
- **Triggers**: On every PR and push to main/master
- **Purpose**: Generates detailed test coverage reports
- **Why**: Helps identify untested code paths

## How to Use

All workflows run automatically when you:
- Create or update a pull request
- Push to main/master branch

You can view workflow results in the **Actions** tab of your GitHub repository.

## Local Testing

Before pushing, you can run these checks locally:

```bash
# Run tests
pytest

# Check code formatting
black --check app/ tests/

# Lint code
ruff check app/ tests/

# Build Docker image
docker build -t test-build .

# Check dependencies
pip install safety && safety check --file requirements.txt
```
