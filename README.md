# aria-testing

Accessibility-focused DOM testing library for tdom, built with modern Python 3.14+.

## Overview

`aria-testing` is a Python DOM testing library that provides accessibility-focused query functions for tdom. It follows
the DOM Testing Library philosophy: **"The more your tests resemble the way your software is used, the more confidence
they can give you."**

## Features

✨ **Modern Python 3.14+** - Uses structural pattern matching, PEP 695 generics, and modern type hints
🎯 **Accessibility-first** - Query by role, label text, and semantic attributes
⚡ **High performance** - Optimized traversal with caching and early-exit strategies
🔒 **Type-safe** - Full type annotations with strict type checking
🧪 **Well-tested** - 144 tests, 100% passing, comprehensive coverage

## Installation

```bash
uv add --dev aria-testing
```

## Quick Start

```python
from tdom.processor import html
from aria_testing import get_by_role, get_by_text, get_by_label_text

# Create a tdom structure
document = html(t"""<div>
    <h1>Welcome</h1>
    <nav>
        <a href="/home">Home</a>
    </nav>
    <form>
        <label>Email
            <input type="email" />
        </label>
        <button>Submit</button>
    </form>
</div>""")

# Find elements using accessibility patterns
heading = get_by_role(document, "heading", level=1)
nav = get_by_role(document, "navigation")
link = get_by_role(document, "link", name="Home")
email_input = get_by_label_text(document, "Email")
button = get_by_text(document, "Submit")
```

## Query Types

Queries are prioritized by accessibility best practices:

### 1. **By Role** ⭐ (Most Recommended)
Find elements by their ARIA role - mirrors how screen readers interact with your app.

```python
button = get_by_role(document, "button")
heading = get_by_role(document, "heading", level=1)
link = get_by_role(document, "link", name="Home")
```

### 2. **By Label Text** ⭐
Find form elements by their associated label - how users identify form fields.

```python
username = get_by_label_text(document, "Username")
email = get_by_label_text(document, "Email Address")
```

### 3. **By Text**
Find elements by their text content.

```python
button = get_by_text(document, "Click me")
heading = get_by_text(document, "Welcome")
```

### 4. **By Test ID**
Find elements by `data-testid` attribute - useful when semantic queries aren't possible.

```python
component = get_by_test_id(document, "user-menu")
```

### 5. **By Tag Name**
Find elements by HTML tag name - use sparingly, prefer semantic queries.

```python
all_links = get_all_by_tag_name(document, "a")
```

### 6. **By ID** & **By Class**
Find elements by HTML attributes - available but less recommended.

```python
element = get_by_id(document, "main-content")
buttons = get_all_by_class(document, "btn-primary")
```

## Query Variants

Each query type comes in **four variants** for different use cases:

| Variant | Returns | Not Found | Multiple Found |
|---------|---------|-----------|----------------|
| `get_by_*` | Single element | ❌ Raises error | ❌ Raises error |
| `query_by_*` | Element or None | ✅ Returns None | ❌ Raises error |
| `get_all_by_*` | List of elements | ❌ Raises error | ✅ Returns all |
| `query_all_by_*` | List (possibly empty) | ✅ Returns `[]` | ✅ Returns all |

### When to Use Each

- **`get_by_*`**: When element MUST exist and be unique (most common)
- **`query_by_*`**: When checking if element exists
- **`get_all_by_*`**: When multiple elements MUST exist
- **`query_all_by_*`**: When finding zero or more elements

## Modern Python Features

Built with cutting-edge Python 3.14+ features:

- **Structural pattern matching** (`match`/`case`) for clean conditionals
- **PEP 695 generic functions** for type-safe query factories
- **Modern type hints** (`X | Y` unions, built-in generics)
- **Keyword-only arguments** for clear, readable APIs
- **Walrus operator** (`:=`) for concise, performant code

## Performance

aria-testing is highly optimized for speed with multiple performance strategies:

### Optimization Techniques

- **Two-level caching** - Element list and role computation caching
- **Early-exit strategies** - Stops searching after finding matches
- **Iterative traversal** - Non-recursive DOM traversal for large trees
- **String interning** - Fast identity-based comparisons for common roles
- **Set-based class matching** - O(1) instead of O(n) for class queries

### Benchmark Results

*Measured on December 6, 2024 - Apple M-series CPU, Python 3.14*

**Test Suite Performance**:
- 154 tests complete in **0.07 seconds** ⚡

**Query Performance** (200-element DOM, 100 iterations per query):

| Query Type | Without Caching | With Caching | Speedup |
|------------|----------------|--------------|---------|
| Role queries | 4.1μs | 1.7μs | **2.4x faster** |
| Text queries | 13.4μs | 10.8μs | **1.2x faster** |
| Class queries | 3.2μs | 0.8μs | **4.1x faster** |
| Tag queries | 3.2μs | 3.1μs | **1.0x faster** |
| **Average** | **5.6μs** | **3.6μs** | **1.55x faster** |

**Cache Efficiency**:
- Element list cache: **99.8% hit rate**
- Role cache: **99.5% hit rate**

*Run benchmarks yourself*:
```bash
just benchmark        # General performance
just benchmark-cache  # Caching comparison
```

### Performance Tips

1. **Reuse containers** - Query the same DOM multiple times to benefit from caching
2. **Use appropriate queries** - `query_all_*` gets full caching benefits
3. **Let caching work** - Caches auto-clear between pytest tests

See `CACHING_IMPLEMENTATION.md` for detailed performance analysis.

## Requirements

- Python 3.14+
- tdom

## Documentation

For full documentation, visit [https://t-strings.github.io/aria-testing/](https://t-strings.github.io/aria-testing/).

## License

MIT
