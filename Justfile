# Justfile for aria-testing
# Requires: just, uv, Python 3.14
# All tasks use uv to ensure isolated, reproducible runs.

# Default recipe shows help
default:
    @just --list

# Print environment info
info:
    @echo "Python: $(python --version)"
    @uv --version

# Install project and dev dependencies
install:
    uv sync --all-groups

# Run tests fast
test *ARGS:
    uv run pytest {{ ARGS }}

# Lint (no changes)
lint:
    uv run ruff check .

# Lint and auto-fix
fix:
    uv run ruff check --fix .

# Type checking
typecheck *ARGS:
    uv run pyright {{ ARGS }}

# Build docs
docs:
    uv run sphinx-build -b html docs docs/_build/html

# Build sdist/wheel
build:
    uv build

# Clean build and cache artifacts
clean:
    rm -rf .pytest_cache .ruff_cache .pyright .mypy_cache build dist
    find docs/_build -mindepth 1 -maxdepth 1 -not -name ".gitkeep" -exec rm -rf {} + || true

# Run the same checks as CI
ci:
    just install
    just lint
    just typecheck
    just test
