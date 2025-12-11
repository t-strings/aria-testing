# Query Reference

This page provides comprehensive documentation for all query functions in aria-testing.

## Query Variants

Each query comes in four variants for different use cases:

| Variant          | Returns               | Not Found      | Multiple Found |
|------------------|-----------------------|----------------|----------------|
| `get_by_*`       | Single element        | ❌ Raises error | ❌ Raises error |
| `query_by_*`     | Element or None       | ✅ Returns None | ❌ Raises error |
| `get_all_by_*`   | List of elements      | ❌ Raises error | ✅ Returns all  |
| `query_all_by_*` | List (possibly empty) | ✅ Returns `[]` | ✅ Returns all  |

### When to Use Each

- **`get_by_*`**: When element MUST exist and be unique (most common in tests)
- **`query_by_*`**: When checking if element exists (conditional logic)
- **`get_all_by_*`**: When multiple elements MUST exist
- **`query_all_by_*`**: When finding zero or more elements (exploratory queries)

## Query by Role ⭐

**Most Recommended** - Find elements by their ARIA role, matching how screen readers interact with your app.

```python
from aria_testing import get_by_role, query_by_role, get_all_by_role, query_all_by_role

# Find by role
button = get_by_role(document, "button")
heading = get_by_role(document, "heading", level=1)

# Find by role with accessible name
link = get_by_role(document, "link", name="Home")

# Pattern matching with regex
import re
link = get_by_role(document, "link", name=re.compile(r"Home|About"))
```

### Supported Roles

#### Landmark Roles

Define page structure and navigation:

- `banner` - `<header>` (when not in article/section)
- `complementary` - `<aside>`
- `contentinfo` - `<footer>` (when not in article/section)
- `form` - `<form>` (when has accessible name)
- `main` - `<main>`
- `navigation` - `<nav>`
- `region` - `<section>` (when has accessible name)
- `search` - Search landmark

#### Document Structure Roles

Organize content:

- `article` - `<article>`
- `list` - `<ul>`, `<ol>`
- `listitem` - `<li>`
- `heading` - `<h1>` through `<h6>`
- `table` - `<table>`
- `row` - `<tr>`
- `cell` - `<td>`
- `columnheader` - `<th scope="col">`
- `rowheader` - `<th scope="row">`

#### Widget Roles

Interactive elements:

- `button` - `<button>`, `<input type="button|submit|reset">`
- `checkbox` - `<input type="checkbox">`
- `link` - `<a href="...">`
- `textbox` - `<input type="text">`, `<textarea>`
- `radio` - `<input type="radio">`
- `searchbox` - `<input type="search">`
- `combobox` - `<select>`

### Finding by Name

The `name` parameter matches the element's accessible name:

```python
# Link text becomes accessible name
link = get_by_role(document, "link", name="About")

# aria-label provides accessible name
button = get_by_role(document, "button", name="Close dialog")

# Pattern matching
link = get_by_role(document, "link", name=re.compile(r"Home|About"))
```

### Finding by Level

Headings support a `level` parameter:

```python
# Find specific heading level
h1 = get_by_role(document, "heading", level=1)
h2 = get_by_role(document, "heading", level=2)

# Combine with name
title = get_by_role(document, "heading", level=1, name="Welcome")
```

## Query by Label Text ⭐

**Highly Recommended** - Find form elements by their associated label, matching how users identify form fields.

```python
from aria_testing import get_by_label_text, query_by_label_text

result = html(t"""
<form>
  <label for="username">Username:</label>
  <input id="username" type="text" />

  <label>
    Email:
    <input type="email" />
  </label>
</form>
""")

# Find by associated label
username = get_by_label_text(result, "Username:")
email = get_by_label_text(result, "Email:")

# Pattern matching
username = get_by_label_text(result, re.compile(r"user", re.IGNORECASE))

# Case-insensitive search
email = get_by_label_text(result, "email", exact=False)
```

## Query by Text

Find elements by their text content:

```python
from aria_testing import get_by_text, query_by_text

# Exact match (default)
element = get_by_text(document, "Welcome to our site")

# Pattern matching with regex
import re
element = get_by_text(document, re.compile(r"Welcome.*"))

# Case-insensitive substring match
element = get_by_text(document, "welcome", exact=False)
```

## Query by Tag Name

Find elements by HTML tag name with optional attribute filtering. Useful for non-semantic elements like `<link>`, `<meta>`, `<script>`:

```python
from aria_testing import get_by_tag_name, get_all_by_tag_name

# Find by tag name only
title = get_by_tag_name(document, "title")

# Find with exact attribute matching
favicon = get_by_tag_name(document, "link", attrs={"rel": "icon"})

# Find all matching elements
stylesheets = get_all_by_tag_name(document, "link", attrs={"rel": "stylesheet"})

# Multiple attributes
viewport = get_by_tag_name(document, "meta", attrs={
    "name": "viewport",
    "content": "width=device-width, initial-scale=1"
})
```

### Special Attribute: `in_class`

Use `in_class` for substring matching within the class attribute:

```python
result = html(t"""
<div>
  <header class="pico-layout is-fixed-above-lg header-main">Header</header>
  <div class="is-fixed-above-lg sidebar">Sidebar</div>
</div>
""")

# Find by class substring
fixed_header = get_by_tag_name(result, "header", attrs={"in_class": "is-fixed-above-lg"})

# Combine with other attributes
pico_header = get_by_tag_name(
    result,
    "header",
    attrs={"in_class": "pico-layout"}
)
```

The `in_class` attribute is useful for:
- Multi-class elements with space-separated values
- Framework naming conventions (e.g., `btn-primary`, `is-active`)
- Partial matching rather than exact token equality

## Query by Test ID

An escape hatch for when semantic queries aren't possible:

```python
from aria_testing import get_by_test_id, query_by_test_id

result = html(t"""
<div data-testid="custom-element">
  <span>Content</span>
</div>
""")

element = get_by_test_id(result, "custom-element")

# Query variant returns None if not found
maybe_element = query_by_test_id(result, "missing")
```

:::{note}
Use test IDs sparingly. Prefer queries by role, label, or text that match how users interact with your app.
:::

## Query by ID

Find elements by their HTML `id` attribute:

```python
from aria_testing import get_by_id, query_by_id

result = html(t"""
<div>
  <h1 id="title">Welcome</h1>
  <button id="save">Save</button>
</div>
""")

# Get throws if not found
save_button = get_by_id(result, "save")

# Query returns None if not found
maybe_title = query_by_id(result, "missing")
assert maybe_title is None
```

:::{note}
Only `get_by_id` and `query_by_id` variants exist (no `get_all_*` or `query_all_*`) since IDs should be unique.
:::

## Query by Class

Find elements by a CSS class token (exact token matching in space-separated class attribute):

```python
from aria_testing import (
    get_by_class,
    query_by_class,
    get_all_by_class,
    query_all_by_class,
)

result = html(t"""
<div>
  <h1 class="title hero">Welcome</h1>
  <button class="btn primary">Save</button>
  <div class="button other"></div>
  <p class="btn muted">Another</p>
</div>
""")

# Single element queries (raises if multiple)
save_button = get_by_class(result, "primary")
maybe_title = query_by_class(result, "missing")  # -> None

# Multiple element queries
all_btns = query_all_by_class(result, "btn")  # [<button ...>, <p ...>]
btns_required = get_all_by_class(result, "btn")  # raises if none found

# Token matching: 'btn' does not match 'button'
button_div = query_by_class(result, "button")
assert button_div.attrs["class"] == "button other"
```

:::{warning}
Class queries use **exact token matching**, not substring matching. `"btn"` will not match `"button"`.

For substring matching, use `get_by_tag_name()` with the `in_class` attribute.
:::

## Error Handling

### ElementNotFoundError

Thrown when `get_by_*` or `get_all_by_*` finds no matching elements:

```python
from aria_testing import ElementNotFoundError

try:
    element = get_by_role(container, "button", name="Missing")
except ElementNotFoundError as e:
    print(f"Could not find element: {e}")
```

### MultipleElementsError

Thrown when `get_by_*` or `query_by_*` finds multiple matching elements:

```python
from aria_testing import MultipleElementsError

try:
    element = get_by_role(container, "button")  # Multiple buttons exist
except MultipleElementsError as e:
    print(f"Found multiple elements: {e}")
```

## Utility Functions

### get_text_content

Extract all text content from an element and its descendants:

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
from aria_testing import normalize_text

text = normalize_text("  Hello   World  ")  # "Hello World"
```
