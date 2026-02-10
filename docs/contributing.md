# Contributing to ectop

Thank you for your interest in improving `ectop`!

## Development Environment

We recommend using Conda or Mamba to manage the development environment, as it simplifies the installation of the `ecflow` dependency.

```bash
# Clone the repository
git clone https://github.com/bbakernoaa/ectop.git
cd ectop

# Create the environment
conda env create -f environment.yml
conda activate ectop

# Install the package in editable mode with dev dependencies
pip install -e .[dev]
```

## Coding Standards

- **Python Version**: Required 3.11+.
- **Type Hints**: All function signatures must include type hints.
- **Documentation**: We use **NumPy-style** docstrings.
- **Formatting**: We use `ruff` for linting and formatting.

### Pre-commit Hooks

We use `pre-commit` to ensure code quality. Install the hooks with:

```bash
pre-commit install
```

## Running Tests

`ectop` uses `pytest` and `pytest-asyncio` for testing.

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src
```

Note: Some tests mock the `ecflow` client to avoid requiring a running server.

## Building Documentation

Documentation is built with `mkdocs` and the `mkdocs-material` theme.

```bash
# Install doc dependencies
pip install -e .[docs]

# Serve the documentation locally
mkdocs serve
```

## Pull Request Process

1.  Create a new branch for your feature or bugfix.
2.  Ensure all tests pass and linting is clean.
3.  Include unit tests for any new functionality.
4.  Update the documentation if you change the API or usage.
5.  Submit a Pull Request to the `main` branch.
