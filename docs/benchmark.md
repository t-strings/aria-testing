# Performance Benchmarks

Real-world performance measurements for aria-testing query operations.

## Overview

aria-testing is optimized for speed with a focus on practical performance. All measurements are taken on real DOM structures with 200+ elements to reflect typical testing scenarios.

## Latest Benchmark Results

*Measured on December 11, 2024 - Apple M-series CPU, Python 3.14*

### Query Performance

200-element DOM structure, 100 iterations per query:

| Query Type                  | Time per Query | Performance Rating |
|-----------------------------|----------------|-------------------|
| `query_all_by_role('link')` | 3.7μs         | ✅ Excellent       |
| `query_all_by_role('heading')` | 3.6μs      | ✅ Excellent       |
| `query_all_by_role(name=...)` | 3.6μs       | ✅ Excellent       |
| `query_all_by_text('text')` | 13.3μs        | ✅ Excellent       |
| `query_all_by_class('cls')` | 3.1μs         | ✅ Excellent       |
| `query_all_by_tag_name('a')` | 3.1μs        | ✅ Excellent       |
| **Average**                 | **4.8μs**     | ✅ **Excellent**   |

### Test Suite Performance

- **179 tests** complete in **0.78 seconds** (parallel mode)
- **Average: 4.4ms per test**
- Includes DOM creation, queries, and assertions

## Performance Targets

aria-testing uses these performance targets:

- ✅ **Excellent**: <30μs per query
- ✅ **Good**: 30-50μs per query
- ⚠️ **Acceptable**: 50-100μs per query
- ❌ **Needs Improvement**: >100μs per query

**Current Status**: ✅ All queries are in the "Excellent" range

## Optimization Strategies

aria-testing achieves high performance through:

### 1. Early Exit Strategies

Queries stop as soon as they have enough results:

```python
def get_by_role(container, role):
    """Stop after finding 2 elements to report error."""
    results = []
    for element in traverse(container):
        if matches_role(element, role):
            results.append(element)
            if len(results) == 2:
                raise MultipleElementsError(...)  # Exit early
```

**Impact**: 10-30% speedup when element appears early in tree.

### 2. Iterative Traversal

Non-recursive DOM traversal using explicit stack:

```python
def traverse_dom(container):
    """Iterative depth-first traversal."""
    elements = []
    stack = [container]

    while stack:
        node = stack.pop()
        if isinstance(node, Element):
            elements.append(node)
            stack.extend(reversed(node.children))

    return elements
```

**Benefits**:
- No recursion depth limit
- Better CPU cache locality
- 5-15% faster than recursive traversal
- Handles deep DOM trees without stack overflow

### 3. String Interning

Common role strings are interned for fast identity checks:

```python
# Module-level interned strings
ROLE_BUTTON = sys.intern("button")
ROLE_LINK = sys.intern("link")

# Fast identity comparison
if computed_role is ROLE_BUTTON:  # O(1) pointer comparison
    handle_button(element)
```

**Benefits**:
- Identity checks (`is`) faster than equality checks (`==`)
- Reduced memory footprint
- Most impactful for frequently used roles

### 4. Set-Based Class Matching

Convert space-separated classes to sets for O(1) lookups:

```python
def has_class(element, class_name):
    """O(1) class token lookup using sets."""
    class_attr = element.attrs.get("class", "")
    class_set = set(class_attr.split())
    return class_name in class_set  # O(1) lookup
```

**Benefits**:
- O(1) lookup instead of O(n) substring search
- Handles multi-class elements efficiently

### 5. Lazy Evaluation

Defer expensive operations until actually needed:

```python
def find_by_role(container, role, *, name=None):
    # First: Filter by role (cheap)
    elements = [e for e in get_all_elements(container)
                if compute_role(e) == role]

    # Only compute accessible names if filtering by name
    if name is not None:
        elements = [e for e in elements
                    if matches_name(compute_name(e), name)]

    return elements
```

**Benefits**:
- Skips expensive operations when not needed
- Name computation only for role-matched elements
- 20-40% speedup when `name` parameter not used

## Running Benchmarks

### General Performance Benchmark

```bash
just benchmark
```

This runs the standard benchmark suite with a 200-element DOM and reports:
- Time per query for each query type
- Average query time
- Performance rating

### Profile Specific Operations

```bash
# Profile query operations with detailed breakdown
just profile-queries

# Profile the entire test suite
just profile-tests
```

### Custom Benchmarking

Create your own benchmarks:

```python
import time
from tdom.processor import html
from aria_testing import query_all_by_role

# Create test DOM
document = html(t"""<div>
    <button>One</button>
    <button>Two</button>
    <!-- Add many more elements -->
</div>""")

# Benchmark
iterations = 100
start = time.perf_counter()
for _ in range(iterations):
    buttons = query_all_by_role(document, "button")
end = time.perf_counter()

avg_time = (end - start) / iterations
print(f"Average time: {avg_time * 1_000_000:.2f}μs")
```

## Performance by DOM Size

Query performance scales linearly with DOM tree size:

| DOM Elements | Average Query Time | Complexity |
|--------------|-------------------|------------|
| 10           | ~1μs              | O(n)       |
| 50           | ~2μs              | O(n)       |
| 100          | ~3μs              | O(n)       |
| 200          | ~5μs              | O(n)       |
| 500          | ~12μs             | O(n)       |
| 1000         | ~24μs             | O(n)       |

**Complexity**: O(n) where n is tree size, with low constant factor.

## Best Practices for Performance

### 1. Scope Queries Appropriately

Query from the smallest container that includes your target:

```python
# ✅ Good - scoped to form, searches ~10 elements
form = get_by_role(document, "form")
submit = get_by_role(form, "button", name="Submit")

# ❌ Less efficient - searches entire document (~200 elements)
submit = get_by_role(document, "button", name="Submit")
```

**Impact**: Linear speedup proportional to tree size reduction.

### 2. Use Specific Queries

More specific queries can exit early:

```python
# ✅ Good - name filter applied during traversal
button = get_by_role(document, "button", name="Submit")

# ❌ Less efficient - finds all buttons, then filters
buttons = get_all_by_role(document, "button")
submit = next(b for b in buttons if "Submit" in get_text_content(b))
```

**Impact**: 10-30% speedup from early exit.

### 3. Leverage pytest Fixtures

Cache expensive component rendering:

```python
import pytest

@pytest.fixture
def navigation_component():
    """Cached navigation rendering."""
    return render_navigation()  # Expensive

def test_nav_structure(navigation_component):
    nav = get_by_role(navigation_component, "navigation")
    assert nav

def test_nav_links(navigation_component):
    # Reuses same cached component
    links = get_all_by_role(navigation_component, "link")
    assert len(links) == 3
```

**Impact**: Eliminates re-rendering overhead between tests.

## Comparison: With vs. Without Optimizations

| Optimization | Impact | When It Matters |
|--------------|--------|-----------------|
| Early exit   | 10-30% | Single-element queries |
| Iterative traversal | 5-15% | Large/deep trees |
| String interning | 2-5% | Role-heavy queries |
| Set-based class matching | 5-10% | Class queries |
| Lazy evaluation | 20-40% | When optional params unused |

## Thread-Safety & Concurrency

aria-testing is **fully thread-safe** and works correctly with:
- Python 3.14's free-threaded interpreter
- Parallel test runners (pytest-xdist)
- Concurrent test execution

All query operations use function-local variables with no shared mutable state, making concurrent access safe without locks.

## See Also

- [Architecture](architecture.md) - System design and implementation details
- [Contributing](contributing.md) - How to contribute performance improvements
- Benchmark source code: `src/aria_testing/profiling/benchmark.py`
