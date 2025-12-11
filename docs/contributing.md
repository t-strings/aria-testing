# Contributing

Guide for developers contributing to aria-testing.

## Development Setup

### Prerequisites

- Python 3.14t (free-threaded build)
- [uv](https://docs.astral.sh/uv/) package manager
- [just](https://just.systems/) command runner

### Installation

```bash
# Clone the repository
git clone https://github.com/t-strings/aria-testing.git
cd aria-testing

# Install dependencies and set up development environment
just install

# Verify setup
just ci-checks
```

## Development Workflow

### Using Just Recipes

The project uses `just` for all development tasks. Run `just` to see all available recipes:

```bash
just
```

Common recipes:

```bash
# Code quality
just lint          # Check for linting issues
just lint-fix      # Auto-fix linting issues
just fmt           # Auto-format code
just fmt-check     # Check formatting without changes
just typecheck     # Run type checking

# Testing
just test                # Run tests (sequential)
just test-parallel       # Run tests (parallel with pytest-xdist)
just test-freethreaded   # Run thread safety tests (8 threads x 10 iterations)

# Quality checks
just ci-checks     # Run all checks (lint, format, typecheck, tests)
just ci-checks-ft  # All checks + free-threading safety tests

# Documentation
just docs          # Build documentation

# Benchmarking
just benchmark        # Run performance benchmarks
just benchmark-cache  # Run caching benchmarks
just profile-queries  # Profile query operations
just profile-tests    # Profile test suite

# Cleanup
just clean         # Remove build artifacts and caches
```

### Development Loop

1. Make your changes
2. Run quick checks: `just lint` and `just typecheck`
3. Run tests: `just test`
4. Run full CI suite: `just ci-checks`
5. Commit when all checks pass

## Code Standards

### Modern Python (3.14+)

Use modern Python features:

**Structural pattern matching:**
```python
match node:
    case Element() as elem:
        process_element(elem)
    case Fragment() as frag:
        process_fragment(frag)
    case Text() as text:
        process_text(text)
```

**PEP 604 union syntax:**
```python
# ✅ Good
def query(container: Element | Fragment | Node) -> Element | None:
    ...

# ❌ Old style
from typing import Union, Optional
def query(container: Union[Element, Fragment, Node]) -> Optional[Element]:
    ...
```

**Built-in generics:**
```python
# ✅ Good
def get_all(container: Element) -> list[Element]:
    ...

# ❌ Old style
from typing import List
def get_all(container: Element) -> List[Element]:
    ...
```

**PEP 695 generic functions:**
```python
# ✅ Good
def make_query[T](finder: Callable[[T], list[Element]]) -> Query[T]:
    ...

# ❌ Old style
from typing import TypeVar, Generic
T = TypeVar('T')
def make_query(finder: Callable[[T], list[Element]]) -> Query[T]:
    ...
```

### Type Hints

All code must have complete type hints:

```python
# ✅ Good - complete type hints
def get_by_role(
    container: Element | Fragment | Node,
    role: str,
    /,
    *,
    name: str | re.Pattern[str] | None = None,
    level: int | None = None,
) -> Element:
    ...

# ❌ Bad - missing type hints
def get_by_role(container, role, name=None, level=None):
    ...
```

### Code Style

- **Formatting**: Use `ruff format` (runs via `just fmt`)
- **Linting**: Use `ruff check` (runs via `just lint`)
- **Line length**: 100 characters (configured in `pyproject.toml`)
- **Docstrings**: Use Google-style docstrings for public APIs

Example docstring:
```python
def get_by_role(
    container: Element | Fragment | Node,
    role: str,
    /,
    *,
    name: str | re.Pattern[str] | None = None,
    level: int | None = None,
) -> Element:
    """Find a single element by ARIA role.

    Args:
        container: Root element/fragment/node to search within.
        role: ARIA role name (e.g., "button", "link", "heading").
        name: Optional accessible name to match (string or regex).
        level: Optional heading level (1-6, only for role="heading").

    Returns:
        The matching Element.

    Raises:
        ElementNotFoundError: When no elements match.
        MultipleElementsError: When multiple elements match.

    Examples:
        >>> button = get_by_role(document, "button")
        >>> heading = get_by_role(document, "heading", level=1)
        >>> link = get_by_role(document, "link", name="Home")
    """
```

## Testing Guidelines

### Test Structure

Place tests in `tests/` directory:

```
tests/
├── conftest.py           # Shared fixtures
├── test_queries.py       # Query function tests
├── test_cache.py         # Cache system tests
├── test_errors.py        # Error handling tests
└── test_utils.py         # Utility function tests
```

### Test Naming

Use descriptive names: `test_<functionality>_<scenario>`

```python
# ✅ Good - clear what's being tested
def test_get_by_role_finds_button():
    ...

def test_get_by_role_raises_when_not_found():
    ...

def test_get_by_role_raises_when_multiple_found():
    ...

# ❌ Bad - unclear
def test_role():
    ...

def test_error():
    ...
```

### Test Coverage

When adding features, test:

1. **Happy path** - Normal usage
2. **Edge cases** - Empty, None, unusual inputs
3. **Error cases** - Invalid inputs, not found, multiple found
4. **Type handling** - Different container types (Element, Fragment, Node)
5. **Pattern matching** - String and regex patterns

Example:
```python
def test_get_by_text_exact_match():
    """Test exact text matching (happy path)."""
    doc = html(t'<div><p>Hello World</p></div>')
    element = get_by_text(doc, "Hello World")
    assert element.tag == "p"


def test_get_by_text_pattern_match():
    """Test regex pattern matching (edge case)."""
    doc = html(t'<div><p>Hello World</p></div>')
    element = get_by_text(doc, re.compile(r"Hello.*"))
    assert element.tag == "p"


def test_get_by_text_not_found():
    """Test error when text not found (error case)."""
    doc = html(t'<div><p>Hello</p></div>')
    with pytest.raises(ElementNotFoundError):
        get_by_text(doc, "Goodbye")


def test_get_by_text_multiple_found():
    """Test error when multiple matches (error case)."""
    doc = html(t'<div><p>Hello</p><p>Hello</p></div>')
    with pytest.raises(MultipleElementsError):
        get_by_text(doc, "Hello")
```

### Running Tests

```bash
# Run all tests
just test

# Run specific test file
just test tests/test_queries.py

# Run specific test function
just test tests/test_queries.py::test_get_by_role_finds_button

# Run tests in parallel
just test-parallel

# Run with coverage
just test --cov
```

### Thread Safety Testing

aria-testing is designed for Python 3.14's free-threaded mode (no GIL). All code must be thread-safe.

#### Testing for Thread Safety

Use `pytest-freethreaded` to detect race conditions and threading issues:

```bash
# Run thread safety tests (8 threads, 10 iterations)
just test-freethreaded

# Custom thread/iteration counts
pytest --threads=16 --iterations=50 --require-gil-disabled tests/

# Test specific concurrency tests
pytest tests/test_concurrency.py -v
```

#### What Gets Tested

The `--threads` and `--iterations` options:
- Run each test multiple times (`--iterations=10`)
- Run tests concurrently across threads (`--threads=8`)
- Expose race conditions, deadlocks, and non-deterministic behavior

Example:
```bash
# This test will run 80 times total (8 threads × 10 iterations)
pytest tests/test_queries.py::test_get_by_role --threads=8 --iterations=10
```

#### Writing Thread-Safe Tests

**✅ Good - No shared mutable state:**
```python
def test_concurrent_queries():
    # Each test creates its own container - thread-safe
    doc = html(t'<div><button>Click</button></div>')
    button = get_by_role(doc, "button")
    assert button.tag == "button"
```

**⚠️ Careful - Shared containers are OK if read-only:**
```python
# Module-level container (created once)
SAMPLE_DOC = html(t'<div><button>Click</button></div>')

def test_read_only_access():
    # Read-only access to shared container - thread-safe
    button = get_by_role(SAMPLE_DOC, "button")
    assert button.tag == "button"
```

**❌ Bad - Shared mutable state:**
```python
# Module-level mutable list - NOT thread-safe!
results = []

def test_with_shared_state():
    # Multiple threads modifying same list - race condition!
    element = get_by_role(doc, "button")
    results.append(element)  # ❌ NOT THREAD-SAFE
```

#### Thread Safety Guidelines

1. **No global mutable state** - Use function-local variables
2. **Immutable data structures** - Use `MappingProxyType`, tuples, frozensets
3. **No caching without locks** - Caching creates shared mutable state
4. **Document thread-safety** - Mark functions as thread-safe in docstrings

See `tests/test_concurrency.py` for examples of proper thread-safe testing.

## Adding New Features

### Adding a New Query Type

1. **Implement the finder function:**

```python
# src/aria_testing/queries/by_custom.py
def _find_by_custom(
    container: Element | Fragment | Node,
    custom_attr: str,
) -> list[Element]:
    """Find all elements matching custom attribute."""
    elements = get_all_elements(container)
    return [
        elem for elem in elements
        if elem.attrs.get("data-custom") == custom_attr
    ]
```

2. **Create query variants using factory:**

```python
from aria_testing.queries.factory import make_query_functions

# Generate all four variants
_custom_queries = make_query_functions(find_elements=_find_by_custom)

get_by_custom = _custom_queries.get_by
query_by_custom = _custom_queries.query_by
get_all_by_custom = _custom_queries.get_all
query_all_by_custom = _custom_queries.query_all
```

3. **Export from main module:**

```python
# src/aria_testing/__init__.py
from aria_testing.queries.by_custom import (
    get_by_custom,
    query_by_custom,
    get_all_by_custom,
    query_all_by_custom,
)
```

4. **Write tests:**

```python
# tests/test_custom.py
def test_get_by_custom_finds_element():
    doc = html(t'<div data-custom="foo">Content</div>')
    element = get_by_custom(doc, "foo")
    assert element.tag == "div"


def test_get_by_custom_not_found():
    doc = html(t'<div>Content</div>')
    with pytest.raises(ElementNotFoundError):
        get_by_custom(doc, "foo")
```

5. **Add documentation** in `docs/queries.md`

6. **Run checks:**

```bash
just ci-checks
```

### Adding a New ARIA Role

1. **Update role mapping:**

```python
# src/aria_testing/roles/mapping.py
TAG_TO_ROLE = {
    # ... existing mappings
    "custom-element": "custom-role",
}
```

2. **Update role computation if needed:**

```python
# src/aria_testing/roles/compute.py
def compute_role(element: Element) -> str | None:
    match element.tag.lower():
        case "custom-element":
            # Custom logic for role computation
            if element.attrs.get("type") == "special":
                return "special-role"
            return "custom-role"
        case _:
            return TAG_TO_ROLE.get(element.tag.lower())
```

3. **Write tests:**

```python
# tests/test_roles.py
def test_custom_element_has_custom_role():
    elem = html(t'<custom-element>Content</custom-element>')
    role = compute_role(elem)
    assert role == "custom-role"
```

4. **Update documentation** in `docs/queries.md` (Supported Roles section)

5. **Run checks:**

```bash
just ci-checks
```

## Performance Considerations

### Optimization Guidelines

1. **Use caching** - Add `@lru_cache` for expensive computations
2. **Early exit** - Stop searching when you have enough results
3. **Lazy evaluation** - Defer expensive operations until needed
4. **Iterative not recursive** - Use explicit stacks for tree traversal
5. **Set-based lookups** - Use sets for O(1) membership checks

### Benchmarking Changes

Always benchmark performance-critical changes:

```bash
# Run benchmarks before changes
just benchmark > before.txt

# Make your changes

# Run benchmarks after changes
just benchmark > after.txt

# Compare
diff before.txt after.txt
```

### Profiling

Profile code to find bottlenecks:

```bash
# Profile query operations
just profile-queries

# Profile full test suite
just profile-tests
```

## Documentation

### Building Docs

```bash
# Build documentation
just docs

# View locally
open docs/_build/html/index.html
```

### Documentation Structure

- `docs/index.md` - Landing page (includes README)
- `docs/queries.md` - Query reference
- `docs/examples.md` - Usage examples
- `docs/api.md` - API reference
- `docs/best-practices.md` - Testing guidelines
- `docs/architecture.md` - Design documentation
- `docs/performance.md` - Performance details
- `docs/contributing.md` - This file

### Writing Documentation

- Use MyST Markdown syntax
- Include code examples with syntax highlighting
- Add type hints to function signatures
- Link related sections with `[text](page.md)`
- Use admonitions for notes, warnings, tips:

```markdown
:::{note}
This is a note.
:::

:::{warning}
This is a warning.
:::

:::{tip}
This is a tip.
:::
```

## Pull Request Process

1. **Fork and clone** the repository
2. **Create a branch** for your feature: `git checkout -b feature/my-feature`
3. **Make changes** following code standards
4. **Write tests** for your changes
5. **Run checks**: `just ci-checks` (all must pass)
6. **Commit changes** with clear messages
7. **Push to your fork**: `git push origin feature/my-feature`
8. **Open a pull request** against the `main` branch

### PR Checklist

- [ ] All tests pass (`just test`)
- [ ] Type checking passes (`just typecheck`)
- [ ] Linting passes (`just lint`)
- [ ] Formatting is correct (`just fmt-check`)
- [ ] Documentation is updated
- [ ] Benchmarks show no regression (for performance changes)
- [ ] CHANGELOG.md is updated (for user-facing changes)

## Git Hooks

Enable pre-push hooks to run CI checks before pushing:

```bash
just enable-pre-push
```

This runs `just ci-checks` before every push, catching issues early.

To disable:

```bash
just disable-pre-push
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/t-strings/aria-testing/issues)
- **Discussions**: [GitHub Discussions](https://github.com/t-strings/aria-testing/discussions)
- **Documentation**: [https://t-strings.github.io/aria-testing/](https://t-strings.github.io/aria-testing/)

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to improve the library and help each other.

## See Also

- [Architecture](architecture.md) - System design and implementation
- [Performance](performance.md) - Performance optimization techniques
- [Best Practices](best-practices.md) - Testing guidelines
