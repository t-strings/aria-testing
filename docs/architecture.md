# Architecture & Design

Deep dive into the design and implementation of aria-testing.

## Overview

aria-testing is built around three core systems:

1. **Query System** - Factory-based query generation with four variants per query type
2. **Role Mapping** - ARIA role to HTML element mapping with accessible name computation
3. **Traversal Engine** - Iterative DOM tree traversal with caching

## Query System Design

### Query Factory Pattern

All queries follow a consistent pattern using PEP 695 generic functions:

```python
def make_query_functions[T](
    *,
    find_elements: Callable[[Container], list[Element]],
) -> QueryFunctions[T]:
    """Factory to create all four query variants."""

    def get_by(...) -> Element:
        elements = find_elements(container)
        if len(elements) == 0:
            raise ElementNotFoundError(...)
        if len(elements) > 1:
            raise MultipleElementsError(...)
        return elements[0]

    def query_by(...) -> Element | None:
        elements = find_elements(container)
        if len(elements) == 0:
            return None
        if len(elements) > 1:
            raise MultipleElementsError(...)
        return elements[0]

    def get_all_by(...) -> list[Element]:
        elements = find_elements(container)
        if len(elements) == 0:
            raise ElementNotFoundError(...)
        return elements

    def query_all_by(...) -> list[Element]:
        return find_elements(container)

    return QueryFunctions(get_by, query_by, get_all_by, query_all_by)
```

### Benefits of Factory Pattern

- **Single source of truth** - Logic defined once, four variants generated
- **Type safety** - Full type hints with generic functions
- **Consistency** - All queries behave the same way
- **Maintainability** - Changes to error handling apply to all queries

### Query Implementation Example

```python
# Define the search logic
def find_by_role_impl(
    container: Container,
    role: str,
    *,
    name: str | Pattern | None = None,
    level: int | None = None,
) -> list[Element]:
    elements = get_all_elements(container)
    return [
        elem for elem in elements
        if matches_role(elem, role, name, level)
    ]

# Generate all four variants
role_queries = make_query_functions(find_elements=find_by_role_impl)

# Export with consistent naming
get_by_role = role_queries.get_by
query_by_role = role_queries.query_by
get_all_by_role = role_queries.get_all
query_all_by_role = role_queries.query_all
```

## Role Mapping System

### Role Computation

The role system maps HTML elements to ARIA roles:

```python
def compute_role(element: Element) -> str | None:
    """Compute the implicit or explicit ARIA role of an element."""

    # Explicit role (aria-role attribute)
    if explicit_role := element.attrs.get("role"):
        return explicit_role

    # Implicit roles based on tag and attributes
    tag = element.tag.lower()

    match tag:
        case "button" | "a" if "href" in element.attrs:
            return tag_to_role[tag]
        case "h1" | "h2" | "h3" | "h4" | "h5" | "h6":
            return "heading"
        case "input":
            return input_type_to_role.get(
                element.attrs.get("type", "text"),
                "textbox"
            )
        case _:
            return tag_to_role.get(tag)
```

### Role Mapping Tables

Efficient role lookups using string interning:

```python
# Landmark roles
TAG_TO_ROLE = {
    "nav": "navigation",
    "main": "main",
    "aside": "complementary",
    "header": "banner",  # context-dependent
    "footer": "contentinfo",  # context-dependent
}

# Input type roles
INPUT_TYPE_TO_ROLE = {
    "button": "button",
    "checkbox": "checkbox",
    "radio": "radio",
    "text": "textbox",
    "email": "textbox",
    "search": "searchbox",
}
```

### Accessible Name Computation

Accessible names come from multiple sources, in priority order:

1. `aria-label` attribute
2. `aria-labelledby` reference
3. Associated `<label>` element (for form inputs)
4. Text content (for links, buttons)
5. `alt` attribute (for images)
6. `title` attribute (fallback)

```python
def compute_accessible_name(element: Element) -> str:
    """Compute accessible name per ARIA specification."""

    # 1. aria-label
    if label := element.attrs.get("aria-label"):
        return normalize_text(label)

    # 2. aria-labelledby
    if labelledby := element.attrs.get("aria-labelledby"):
        # Look up referenced element(s)
        return compute_referenced_name(labelledby)

    # 3. Label association (for form controls)
    if element.tag == "input":
        if label := find_associated_label(element):
            return get_text_content(label)

    # 4. Text content
    return normalize_text(get_text_content(element))
```

### Heading Level Computation

Special handling for heading elements:

```python
def compute_heading_level(element: Element) -> int | None:
    """Get the heading level (1-6) if element is a heading."""

    match element.tag.lower():
        case "h1": return 1
        case "h2": return 2
        case "h3": return 3
        case "h4": return 4
        case "h5": return 5
        case "h6": return 6
        case _:
            # Check aria-level attribute
            if level := element.attrs.get("aria-level"):
                return int(level)
            return None
```

## Traversal Engine

### Iterative Traversal

Non-recursive iterative traversal for performance and stack safety:

```python
def get_all_elements(container: Container) -> list[Element]:
    """Get all elements using iterative traversal."""

    elements: list[Element] = []
    stack: list[Node] = [container]

    while stack:
        node = stack.pop()

        match node:
            case Element() as elem:
                elements.append(elem)
                # Add children in reverse order (for depth-first)
                stack.extend(reversed(elem.children))
            case Fragment() as frag:
                stack.extend(reversed(frag.children))
            case Text():
                pass  # Skip text nodes

    return elements
```

**Benefits:**
- No recursion depth limit
- Better performance for deep trees
- Explicit stack management

### Early Exit Optimization

Queries stop as soon as they have enough matches:

```python
def find_with_early_exit(
    container: Container,
    predicate: Callable[[Element], bool],
    *,
    max_results: int | None = None,
) -> list[Element]:
    """Find elements with early exit when max_results reached."""

    results = []
    stack = [container]

    while stack:
        node = stack.pop()

        if isinstance(node, Element):
            if predicate(node):
                results.append(node)
                # Early exit for single-element queries
                if max_results and len(results) >= max_results:
                    return results

            stack.extend(reversed(node.children))

    return results
```

**Used by:**
- `get_by_*` - exits after finding 2 elements (to report error)
- `query_by_*` - exits after finding 2 elements (to report error)
- `get_all_by_*` and `query_all_by_*` - traverse full tree

## Caching System

### Two-Level Cache

aria-testing uses two cache levels:

**Level 1: Element List Cache**
- Caches `get_all_elements()` results by container ID
- Avoids re-traversing the same DOM tree
- 99.8% hit rate in benchmarks

**Level 2: Role Cache**
- Caches computed roles by element ID
- Avoids recomputing roles for same elements
- 99.5% hit rate in benchmarks

### Cache Implementation

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_all_elements_cached(container: Container) -> list[Element]:
    """Cached element traversal."""
    return _get_all_elements_uncached(container)

@lru_cache(maxsize=512)
def compute_role_cached(element: Element) -> str | None:
    """Cached role computation."""
    return _compute_role_uncached(element)
```

### Cache Invalidation

Caches are automatically cleared:
- Between pytest test functions (via fixture)
- When explicitly requested (`clear_caches()`)

```python
import pytest
from aria_testing.cache import clear_caches

@pytest.fixture(autouse=True)
def clear_aria_testing_caches():
    """Clear caches between tests."""
    clear_caches()
    yield
    clear_caches()
```

### Cache Statistics

Runtime cache statistics available for debugging:

```python
from aria_testing.cache import get_cache_stats

stats = get_cache_stats()
print(f"Element cache: {stats.element_list.hit_rate:.1%} hit rate")
print(f"Role cache: {stats.role.hit_rate:.1%} hit rate")
```

## Type System

### Modern Type Hints

Full use of Python 3.14+ type features:

```python
# PEP 604 union syntax
Container = Element | Fragment | Node
TextMatch = str | re.Pattern[str]

# Built-in generics
def find_elements(container: Container) -> list[Element]: ...

# PEP 695 generic functions
def make_query_functions[T](
    find_elements: Callable[[Container], list[Element]],
) -> QueryFunctions[T]: ...
```

### Structural Pattern Matching

Extensive use of `match`/`case` for clean conditionals:

```python
match node:
    case Element() as elem:
        process_element(elem)
    case Fragment() as frag:
        process_fragment(frag)
    case Text() as text:
        process_text(text)
    case _:
        raise TypeError(f"Unexpected node type: {type(node)}")
```

## Error Handling

### Custom Exceptions

Domain-specific exceptions with helpful messages:

```python
class ElementNotFoundError(Exception):
    """No elements found matching query."""

    def __init__(self, query_description: str):
        super().__init__(
            f"Unable to find element: {query_description}\n\n"
            f"This usually means the element doesn't exist or "
            f"your query is too specific."
        )

class MultipleElementsError(Exception):
    """Multiple elements found when expecting one."""

    def __init__(self, query_description: str, count: int):
        super().__init__(
            f"Found {count} elements matching: {query_description}\n\n"
            f"Use get_all_by_* or query_all_by_* to find multiple elements, "
            f"or make your query more specific."
        )
```

### Error Messages

Detailed error messages help debugging:

```python
# Example error output
"""
ElementNotFoundError: Unable to find element: role="button" name="Submit"

This usually means the element doesn't exist or your query is too specific.

Possible issues:
- Element role is different than expected
- Accessible name doesn't match (check aria-label, text content)
- Element is not in the container you're searching
"""
```

## Performance Optimizations

### String Interning

Role strings are interned for fast identity comparisons:

```python
# Interned role strings
ROLE_BUTTON = "button"
ROLE_LINK = "link"
ROLE_HEADING = "heading"

# Fast identity comparison (not equality)
if role is ROLE_BUTTON:  # Faster than role == "button"
    ...
```

### Set-Based Class Matching

O(1) class token lookups:

```python
def matches_class(element: Element, class_name: str) -> bool:
    """Check if element has class token in its class attribute."""
    class_attr = element.attrs.get("class", "")
    class_set = set(class_attr.split())
    return class_name in class_set  # O(1) lookup
```

### Lazy Evaluation

Defer expensive operations until needed:

```python
def get_by_role(container, role, *, name=None):
    # Don't compute accessible names unless filtering by name
    elements = [e for e in get_all_elements(container) if matches_role(e, role)]

    if name is not None:
        # Only compute names when needed
        elements = [e for e in elements if matches_name(e, name)]

    return validate_single_element(elements)
```

## Design Principles

1. **Accessibility First** - Encourage accessible HTML through query design
2. **Performance** - Optimize for common cases with caching and early exit
3. **Type Safety** - Full type hints and static checking
4. **Fail Fast** - Clear errors at the point of failure
5. **Consistency** - All queries follow the same patterns
6. **Modern Python** - Use latest language features (3.14+)

## See Also

- [Performance](performance.md) - Detailed performance analysis and benchmarks
- [API Reference](api.md) - Complete function signatures
- [Contributing](contributing.md) - How to extend the library
