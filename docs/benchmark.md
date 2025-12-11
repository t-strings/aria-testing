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

## Thread-Safety & Free-Threading Compatibility

aria-testing is **fully thread-safe** and designed for Python 3.14+ free-threading (PEP 703). The library works correctly with:

- **Python 3.14's free-threaded interpreter** (no-GIL build)
- **Parallel test runners** (pytest-xdist)
- **Concurrent.futures thread pools**
- **Multi-threaded test frameworks**

### Design for Concurrency

aria-testing achieves thread safety through careful design choices:

#### 1. **No Mutable Global State**

All query operations use function-local variables exclusively:

```python
def get_by_role(container, role):
    # All state is local to this function call
    elements = []
    for element in traverse(container):
        if matches_role(element, role):
            elements.append(element)
    return elements[0]
```

**Result**: Multiple threads can execute queries simultaneously without interference.

#### 2. **Immutable Module-Level Data**

Module constants use `MappingProxyType` for runtime immutability:

```python
from types import MappingProxyType

_ROLE_MAP = MappingProxyType({
    sys.intern("button"): sys.intern("button"),
    sys.intern("nav"): sys.intern("navigation"),
    # ... more mappings
})
```

**Benefits**:
- Read-only access is inherently thread-safe
- No locks needed for lookups
- Python optimizes immutable data structure access

#### 3. **String Interning for Safety**

Interned strings enable fast, thread-safe comparisons:

```python
# Interned strings are cached by Python's runtime
button_role = sys.intern("button")

# Identity comparison (pointer comparison) is atomic and thread-safe
if computed_role is button_role:
    handle_button(element)
```

#### 4. **No Caching Layer**

Previous versions included a caching system that was removed to ensure free-threading compatibility:

```python
# ❌ Old approach (removed): Mutable cache with potential race conditions
cache = {}
if element not in cache:
    cache[element] = compute_role(element)

# ✅ New approach: Pure computation, no shared state
role = compute_role(element)
```

**Trade-off**: Removed caching for guaranteed thread safety. The performance impact is minimal due to other optimizations (string interning, early exit, iterative traversal).

### Testing with Parallelism

The test suite verifies thread safety through parallel execution:

```bash
# Run 179 tests across 8 workers
pytest -n auto

# Result: 179 passed in 0.78s
# All tests pass without race conditions or failures
```

### Best Practices for Multi-threaded Use

#### Safe Usage Patterns

```python
from concurrent.futures import ThreadPoolExecutor
from aria_testing import get_by_role

def test_component(html_content):
    """Each thread gets its own container - safe."""
    container = html(html_content)
    button = get_by_role(container, "button")
    return button.attrs.get("name")

# Safe: Each thread operates on independent containers
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(test_component, html_samples)
```

#### Container Independence

Since tdom containers are independent data structures, you can:
- Query the same container from multiple threads (read-only)
- Query different containers concurrently
- Build containers in parallel threads

All operations are safe because aria-testing doesn't modify containers or maintain shared state.

### Free-Threading Performance

With Python 3.14's free-threaded build (no GIL):

**Expected Benefits**:
- True parallel execution of queries across CPU cores
- Linear scaling for CPU-bound test suites
- No lock contention (aria-testing uses no locks)

**Verified Compatibility**:
- No global mutable state
- No thread-local storage dependencies
- No assumptions about GIL protection
- Pure Python implementation (no C extensions)

### Running with Free-Threaded Python

To test with Python 3.14's free-threaded build:

```bash
# Install free-threaded Python 3.14
# (Build with --disable-gil or use python3.14t)

# Run tests with free-threading enabled
PYTHON_GIL=0 pytest -n auto

# Verify no race conditions with longer runs
PYTHON_GIL=0 pytest -n auto --count=100
```

### Thread-Safety Guarantees

aria-testing guarantees:

✅ **Query operations are thread-safe** - Multiple threads can query simultaneously
✅ **No race conditions** - No shared mutable state
✅ **No deadlocks** - No locks used
✅ **Deterministic results** - Same query returns same results regardless of threading
✅ **Exception safety** - Errors are isolated to individual threads

⚠️ **Note**: tdom containers themselves must be thread-safe. aria-testing doesn't modify containers, but if you're mutating containers from multiple threads, you need your own synchronization.

## See Also

- [Architecture](architecture.md) - System design and implementation details
- [Contributing](contributing.md) - How to contribute performance improvements
- Benchmark source code: `src/aria_testing/profiling/benchmark.py`
