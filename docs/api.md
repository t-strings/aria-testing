# API Reference

Complete function signatures and parameters for all aria-testing query functions.

## Query Function Signatures

All query functions accept a `container` (Element, Fragment, or Node) and return matching elements.

### By Role

```python
get_by_role(
    container: Element | Fragment | Node,
    role: str,
    /,
    *,
    name: str | re.Pattern[str] | None = None,
    level: int | None = None,
) -> Element

query_by_role(
    container: Element | Fragment | Node,
    role: str,
    /,
    *,
    name: str | re.Pattern[str] | None = None,
    level: int | None = None,
) -> Element | None

get_all_by_role(
    container: Element | Fragment | Node,
    role: str,
    /,
    *,
    name: str | re.Pattern[str] | None = None,
    level: int | None = None,
) -> list[Element]

query_all_by_role(
    container: Element | Fragment | Node,
    role: str,
    /,
    *,
    name: str | re.Pattern[str] | None = None,
    level: int | None = None,
) -> list[Element]
```

**Parameters:**
- `container`: The root element/fragment/node to search within
- `role`: ARIA role name (e.g., "button", "link", "heading")
- `name`: Optional accessible name to match (string or regex pattern)
- `level`: Optional heading level (1-6, only valid for role="heading")

**Returns:**
- `get_by_*`: Single Element (raises if zero or multiple found)
- `query_by_*`: Element or None (raises if multiple found)
- `get_all_by_*`: List of Elements (raises if none found)
- `query_all_by_*`: List of Elements (empty list if none found)

**Raises:**
- `ElementNotFoundError`: When `get_by_*` or `get_all_by_*` finds no matches
- `MultipleElementsError`: When `get_by_*` or `query_by_*` finds multiple matches

### By Text

```python
get_by_text(
    container: Element | Fragment | Node,
    text: str | re.Pattern[str],
    /,
    *,
    exact: bool = True,
) -> Element

query_by_text(
    container: Element | Fragment | Node,
    text: str | re.Pattern[str],
    /,
    *,
    exact: bool = True,
) -> Element | None

get_all_by_text(
    container: Element | Fragment | Node,
    text: str | re.Pattern[str],
    /,
    *,
    exact: bool = True,
) -> list[Element]

query_all_by_text(
    container: Element | Fragment | Node,
    text: str | re.Pattern[str],
    /,
    *,
    exact: bool = True,
) -> list[Element]
```

**Parameters:**
- `container`: The root element/fragment/node to search within
- `text`: Text to match (string or regex pattern)
- `exact`: If True, text must match exactly (after normalization). If False, substring matching is used

**Returns/Raises:** Same as role queries

### By Label Text

```python
get_by_label_text(
    container: Element | Fragment | Node,
    text: str | re.Pattern[str],
    /,
    *,
    exact: bool = True,
) -> Element

query_by_label_text(
    container: Element | Fragment | Node,
    text: str | re.Pattern[str],
    /,
    *,
    exact: bool = True,
) -> Element | None

get_all_by_label_text(
    container: Element | Fragment | Node,
    text: str | re.Pattern[str],
    /,
    *,
    exact: bool = True,
) -> list[Element]

query_all_by_label_text(
    container: Element | Fragment | Node,
    text: str | re.Pattern[str],
    /,
    *,
    exact: bool = True,
) -> list[Element]
```

**Parameters:**
- `container`: The root element/fragment/node to search within
- `text`: Label text to match (string or regex pattern)
- `exact`: If True, text must match exactly (after normalization). If False, substring matching is used

**Returns/Raises:** Same as role queries

**Note:** Searches for `<label>` elements and finds their associated form controls via:
1. `for` attribute matching an `id`
2. Label wrapping the input element

### By Tag Name

```python
get_by_tag_name(
    container: Element | Fragment | Node,
    tag: str,
    /,
    *,
    attrs: dict[str, str] | None = None,
) -> Element

query_by_tag_name(
    container: Element | Fragment | Node,
    tag: str,
    /,
    *,
    attrs: dict[str, str] | None = None,
) -> Element | None

get_all_by_tag_name(
    container: Element | Fragment | Node,
    tag: str,
    /,
    *,
    attrs: dict[str, str] | None = None,
) -> list[Element]

query_all_by_tag_name(
    container: Element | Fragment | Node,
    tag: str,
    /,
    *,
    attrs: dict[str, str] | None = None,
) -> list[Element]
```

**Parameters:**
- `container`: The root element/fragment/node to search within
- `tag`: HTML tag name (case-insensitive)
- `attrs`: Optional dictionary of attribute name/value pairs to match
  - Regular attributes use exact string matching
  - Special key `"in_class"` uses substring matching within the class attribute

**Returns/Raises:** Same as role queries

**Examples:**
```python
# Exact attribute matching
favicon = get_by_tag_name(doc, "link", attrs={"rel": "icon"})

# Class substring matching
header = get_by_tag_name(doc, "header", attrs={"in_class": "is-fixed"})

# Multiple attributes
meta = get_by_tag_name(doc, "meta", attrs={
    "name": "viewport",
    "content": "width=device-width"
})
```

### By Test ID

```python
get_by_test_id(
    container: Element | Fragment | Node,
    test_id: str,
    /,
) -> Element

query_by_test_id(
    container: Element | Fragment | Node,
    test_id: str,
    /,
) -> Element | None

get_all_by_test_id(
    container: Element | Fragment | Node,
    test_id: str,
    /,
) -> list[Element]

query_all_by_test_id(
    container: Element | Fragment | Node,
    test_id: str,
    /,
) -> list[Element]
```

**Parameters:**
- `container`: The root element/fragment/node to search within
- `test_id`: Value of the `data-testid` attribute

**Returns/Raises:** Same as role queries

### By ID

```python
get_by_id(
    container: Element | Fragment | Node,
    id: str,
    /,
) -> Element

query_by_id(
    container: Element | Fragment | Node,
    id: str,
    /,
) -> Element | None
```

**Parameters:**
- `container`: The root element/fragment/node to search within
- `id`: Value of the HTML `id` attribute

**Returns/Raises:** Same as single-element queries

**Note:** Only single-element variants exist (no `get_all_*` or `query_all_*`) since IDs should be unique.

### By Class

```python
get_by_class(
    container: Element | Fragment | Node,
    class_name: str,
    /,
) -> Element

query_by_class(
    container: Element | Fragment | Node,
    class_name: str,
    /,
) -> Element | None

get_all_by_class(
    container: Element | Fragment | Node,
    class_name: str,
    /,
) -> list[Element]

query_all_by_class(
    container: Element | Fragment | Node,
    class_name: str,
    /,
) -> list[Element]
```

**Parameters:**
- `container`: The root element/fragment/node to search within
- `class_name`: CSS class token to match (exact token match in space-separated class attribute)

**Returns/Raises:** Same as role queries

**Note:** Uses exact token matching. `"btn"` will not match `"button"`. For substring matching, use `get_by_tag_name()` with `attrs={"in_class": "..."}`.

## Utility Functions

### get_text_content

Extract all text content from an element and its descendants:

```python
def get_text_content(node: Element | Text | Fragment | Node) -> str
```

**Parameters:**
- `node`: Element, Text node, Fragment, or Node to extract text from

**Returns:**
- String containing all text content with normalized whitespace

**Example:**
```python
from aria_testing import get_text_content

element = html(t"""
<div>
  <h1>Title</h1>
  <p>Paragraph text</p>
</div>
""")

text = get_text_content(element)  # "Title Paragraph text"
```

### normalize_text

Normalize whitespace in text (collapse multiple spaces, strip leading/trailing):

```python
def normalize_text(text: str) -> str
```

**Parameters:**
- `text`: String to normalize

**Returns:**
- String with normalized whitespace (single spaces, no leading/trailing whitespace)

**Example:**
```python
from aria_testing import normalize_text

text = normalize_text("  Hello   World  ")  # "Hello World"
```

## Exception Classes

### ElementNotFoundError

```python
class ElementNotFoundError(Exception):
    """Raised when a get_by_* or get_all_by_* query finds no matching elements."""
```

Raised by:
- `get_by_*` when no elements match
- `get_all_by_*` when no elements match

### MultipleElementsError

```python
class MultipleElementsError(Exception):
    """Raised when a get_by_* or query_by_* query finds multiple matching elements."""
```

Raised by:
- `get_by_*` when multiple elements match
- `query_by_*` when multiple elements match

## Type Aliases

```python
from tdom import Element, Fragment, Node, Text

# Container types accepted by all queries
Container = Element | Fragment | Node

# Text matching types
TextMatch = str | re.Pattern[str]

# Query return types (for type hints)
SingleElement = Element
OptionalElement = Element | None
ElementList = list[Element]
```

## See Also

- [Query Reference](queries.md) - Detailed query documentation with examples
- [Examples](examples.md) - Real-world usage patterns
- [Best Practices](best-practices.md) - Testing guidelines
