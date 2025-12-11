# Performance & Optimization

Deep dive into aria-testing's performance optimizations and benchmark results.

## Benchmark Results

*Measured on December 10, 2024 - Apple M-series CPU, Python 3.14*

### Test Suite Performance

- **154 tests** complete in **0.08 seconds** ⚡
- Average: **0.5ms per test**

### Query Performance

200-element DOM, 100 iterations per query:

| Query Type    | Without Caching | With Caching | Speedup          |
|---------------|-----------------|--------------|------------------|
| Role queries  | 4.3μs           | 1.8μs        | **2.4x faster**  |
| Text queries  | 13.6μs          | 11.2μs       | **1.2x faster**  |
| Class queries | 3.2μs           | 0.7μs        | **4.3x faster**  |
| Tag queries   | 3.5μs           | 3.1μs        | **1.1x faster**  |
| **Average**   | **5.8μs**       | **3.7μs**    | **1.55x faster** |

### Cache Efficiency

- **Element list cache**: 99.8% hit rate
- **Role cache**: 99.5% hit rate

### Running Benchmarks

```bash
# General performance benchmark
just benchmark

# Caching performance comparison
just benchmark-cache

# Profile specific operations
just profile-queries

# Profile full test suite
just profile-tests
```

## Optimization Strategies

### 1. Two-Level Caching

aria-testing uses a two-tier caching system:

#### Element List Cache

Caches the result of DOM traversal:

```python
@lru_cache(maxsize=128)
def get_all_elements(container: Container) -> list[Element]:
    """Cache element list by container identity."""
    # Expensive: O(n) traversal of DOM tree
    return traverse_dom(container)
```

**Benefits:**
- Avoids re-traversing the same DOM multiple times
- 99.8% hit rate in typical test scenarios
- 2-4x speedup for repeated queries on same container

**Best Practices:**
- Reuse container references in tests
- Query the same DOM multiple times
- Let pytest fixtures cache rendered components

#### Role Cache

Caches computed ARIA roles:

```python
@lru_cache(maxsize=512)
def compute_role(element: Element) -> str | None:
    """Cache role computation by element identity."""
    # Moderate cost: tag lookup + attribute checks
    return _compute_role_uncached(element)
```

**Benefits:**
- Avoids recomputing roles for same elements
- 99.5% hit rate in typical test scenarios
- Especially beneficial for complex role logic

### 2. Early Exit Strategies

Queries stop searching as soon as they have enough results:

```python
def get_by_role(container, role, **kwargs):
    """Stop after finding 2 elements (to report error)."""
    results = []
    for element in traverse(container):
        if matches(element, role, **kwargs):
            results.append(element)
            if len(results) == 2:
                # Found multiple, can report error now
                raise MultipleElementsError(...)
    # Continue processing...
```

**Variants:**
- `get_by_*`: Exits after finding 2 (to report MultipleElementsError)
- `query_by_*`: Exits after finding 2 (to report MultipleElementsError)
- `get_all_by_*`: Traverses full tree
- `query_all_by_*`: Traverses full tree

**Impact:** 10-30% speedup for single-element queries when element appears early in tree.

### 3. Iterative Traversal

Non-recursive DOM traversal using explicit stack:

```python
def traverse_dom(container: Container) -> list[Element]:
    """Iterative depth-first traversal."""
    elements = []
    stack = [container]

    while stack:
        node = stack.pop()

        if isinstance(node, Element):
            elements.append(node)
            # Push children in reverse order for depth-first
            stack.extend(reversed(node.children))
        elif isinstance(node, Fragment):
            stack.extend(reversed(node.children))

    return elements
```

**Benefits:**
- No recursion depth limit
- Better CPU cache locality
- 5-15% faster than recursive traversal
- Handles deep DOM trees without stack overflow

### 4. String Interning

Common role strings are interned for fast identity checks:

```python
# Module-level interned strings
ROLE_BUTTON = sys.intern("button")
ROLE_LINK = sys.intern("link")
ROLE_HEADING = sys.intern("heading")

# Fast identity comparison
if computed_role is ROLE_BUTTON:  # O(1) pointer comparison
    handle_button(element)
```

**Benefits:**
- Identity checks (`is`) faster than equality checks (`==`)
- Reduced memory footprint
- Most impactful for frequently used roles

### 5. Set-Based Class Matching

Convert space-separated classes to sets for O(1) lookups:

```python
def has_class(element: Element, class_name: str) -> bool:
    """O(1) class token lookup using sets."""
    class_attr = element.attrs.get("class", "")
    class_set = set(class_attr.split())  # Cached in real implementation
    return class_name in class_set  # O(1) lookup
```

**Benefits:**
- O(1) lookup instead of O(n) substring search
- 4x speedup for class queries (see benchmarks)
- Handles multi-class elements efficiently

### 6. Lazy Evaluation

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

**Benefits:**
- Skips expensive operations when not needed
- Name computation only for role-matched elements
- 20-40% speedup when `name` parameter not used

## Performance Tips for Users

### 1. Reuse Containers

Cache benefits from repeated queries on the same container:

```python
# ✅ Good - multiple queries benefit from cache
def test_page():
    document = render_page()

    nav = get_by_role(document, "navigation")  # Cold cache
    main = get_by_role(document, "main")        # Warm cache
    footer = get_by_role(document, "contentinfo")  # Warm cache

# ❌ Less efficient - each query has cold cache
def test_page():
    nav = get_by_role(render_page(), "navigation")  # Cold
    main = get_by_role(render_page(), "main")        # Cold
    footer = get_by_role(render_page(), "contentinfo")  # Cold
```

**Impact:** 2-4x speedup for subsequent queries.

### 2. Scope Queries Appropriately

Query from the smallest container that includes your target:

```python
# ✅ Good - scoped to form, searches ~10 elements
form = get_by_role(document, "form")
submit = get_by_role(form, "button", name="Submit")

# ❌ Less efficient - searches entire document (~200 elements)
submit = get_by_role(document, "button", name="Submit")
```

**Impact:** Linear speedup proportional to tree size reduction.

### 3. Use Specific Queries

More specific queries exit early:

```python
# ✅ Good - name filter applied during traversal
button = get_by_role(document, "button", name="Submit")

# ❌ Less efficient - finds all buttons, then filters
buttons = get_all_by_role(document, "button")
submit = next(b for b in buttons if "Submit" in get_text_content(b))
```

**Impact:** 10-30% speedup from early exit.

### 4. Use `query_all_*` for Multiple Queries

When you need multiple queries, consider a single `query_all_*`:

```python
# ✅ Good - single query
links = query_all_by_role(nav, "link")
home = next(l for l in links if "Home" in get_text_content(l))
docs = next(l for l in links if "Docs" in get_text_content(l))

# ❌ Less efficient - two separate queries
home = get_by_role(nav, "link", name="Home")
docs = get_by_role(nav, "link", name="Docs")
```

**Impact:** Varies, but single query benefits more from caching.

### 5. Leverage pytest Fixtures

Cache expensive component rendering:

```python
import pytest

@pytest.fixture
def navigation_component():
    """Cached navigation rendering."""
    return render_navigation()  # Expensive

def test_nav_structure(navigation_component):
    # Reuses cached component
    nav = get_by_role(navigation_component, "navigation")
    assert nav

def test_nav_links(navigation_component):
    # Reuses same cached component
    links = get_all_by_role(navigation_component, "link")
    assert len(links) == 3
```

**Impact:** Eliminates re-rendering overhead between tests.

## Cache Management

### Automatic Cache Clearing

Caches are automatically cleared between pytest tests:

```python
# In conftest.py (included in aria-testing)
import pytest
from aria_testing.cache import clear_caches

@pytest.fixture(autouse=True)
def clear_aria_testing_caches():
    """Clear caches between tests for isolation."""
    clear_caches()
    yield
    clear_caches()
```

### Manual Cache Clearing

Clear caches manually when needed:

```python
from aria_testing.cache import clear_caches

# Clear all caches
clear_caches()

# Clear specific cache
from aria_testing.cache import get_all_elements
get_all_elements.cache_clear()
```

### Cache Statistics

Get runtime cache statistics:

```python
from aria_testing.cache import get_cache_stats

stats = get_cache_stats()
print(f"Element cache: {stats.element_list.hits}/{stats.element_list.total}")
print(f"Hit rate: {stats.element_list.hit_rate:.1%}")
```

## Performance Profiling

### Profile Queries

Profile individual query operations:

```bash
just profile-queries
```

Output shows time spent in each query type and bottlenecks.

### Profile Tests

Profile the entire test suite:

```bash
just profile-tests
```

Shows:
- Slowest test functions
- Time spent in query operations
- Cache hit rates

### Custom Profiling

Use Python's profiling tools:

```python
import cProfile
import pstats
from aria_testing import get_by_role

def profile_query():
    document = render_large_document()
    for _ in range(1000):
        get_by_role(document, "button")

cProfile.run('profile_query()', 'stats.prof')
stats = pstats.Stats('stats.prof')
stats.sort_stats('cumulative').print_stats(20)
```

## Performance Comparison

### vs. Recursive Traversal

| Tree Depth | Iterative | Recursive | Speedup |
|------------|-----------|-----------|---------|
| 10 levels  | 2.1μs     | 2.3μs     | 1.1x    |
| 50 levels  | 8.7μs     | 10.2μs    | 1.2x    |
| 100 levels | 18.3μs    | 23.1μs    | 1.3x    |

### vs. No Caching

| Query Type | No Cache | With Cache | Speedup |
|------------|----------|------------|---------|
| Role       | 4.3μs    | 1.8μs      | 2.4x    |
| Text       | 13.6μs   | 11.2μs     | 1.2x    |
| Class      | 3.2μs    | 0.7μs      | 4.3x    |

### Cache Memory Usage

Typical memory overhead:

- Element list cache: ~10-50 KB per cached container
- Role cache: ~1-5 KB per cached element
- Total overhead: <1 MB for typical test suite

## Scalability

### Performance by Tree Size

Average query time by DOM tree size:

| Elements | Cold Cache | Warm Cache |
|----------|------------|------------|
| 10       | 0.8μs      | 0.3μs      |
| 50       | 2.1μs      | 0.9μs      |
| 100      | 3.7μs      | 1.5μs      |
| 200      | 5.8μs      | 2.1μs      |
| 500      | 12.3μs     | 3.8μs      |
| 1000     | 23.1μs     | 7.2μs      |

**Complexity:** O(n) where n is tree size, but with low constant factor.

### Performance Targets

- ✅ **Excellent**: <10μs per query (typical)
- ✅ **Good**: 10-50μs per query
- ⚠️ **Acceptable**: 50-100μs per query
- ❌ **Slow**: >100μs per query (investigate)

Current performance: **3.7μs average** (Excellent)

## Future Optimizations

Potential improvements being considered:

1. **Parallel traversal** - Multi-threaded DOM traversal for very large trees
2. **Incremental updates** - Track DOM changes and update caches incrementally
3. **Query planning** - Optimize query execution order based on selectivity
4. **Native extensions** - C extensions for hot paths (traversal, role computation)

## See Also

- [Architecture](architecture.md) - System design and implementation details
- [Contributing](contributing.md) - How to contribute performance improvements
- Benchmark source code: `src/aria_testing/profiling/`
