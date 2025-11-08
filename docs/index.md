# aria_testing: Testing Library for tdom

`aria_testing` is a Python DOM testing library for tdom that provides accessibility-focused query functions. It follows
the DOM Testing Library philosophy: **"The more your tests resemble the way your software is used, the more confidence
they can give you."**

## Overview

The `aria_testing` package provides query functions that work with tdom's `Node`, `Element`, `Text`, and `Fragment`
types. It encourages writing tests that interact with components the way users do—by finding elements through accessible
names, roles, and labels rather than implementation details like CSS classes or element IDs.

## Installation

`aria_testing` is included as part of `tdom-sphinx`:

```python
from aria_testing import get_by_role, get_by_text
```

## Core Concepts

### Query Variants

Each query comes in four variants:

1. **`get_by_*`**: Returns a single element, throws if zero or multiple found
2. **`query_by_*`**: Returns a single element or None, throws if multiple found
3. **`get_all_by_*`**: Returns a list of elements, throws if none found
4. **`query_all_by_*`**: Returns a list of elements (possibly empty)

### Supported Query Types

- **By Role**: Find elements by their ARIA role (most recommended)
- **By Text**: Find elements by their text content
- **By Label Text**: Find form elements by their associated label
- **By Tag Name**: Find elements by HTML tag name with optional attribute filtering
- **By Test ID**: Find elements by `data-testid` attribute (escape hatch)
- **By ID**: Find elements by their HTML `id` attribute (specific targeting)
- **By Class**: Find elements by a CSS class token (space-separated `class` attribute)

## Query by Role

The most recommended way to find elements. It matches how users and assistive technologies identify elements.

```python
from tdom import html
from aria_testing import get_by_role

# Create a component
result = html(t"""
<nav>
  <ul>
    <li><a href="/home">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>
""")

# Find by role
nav = get_by_role(result, "navigation")
link = get_by_role(result, "link", name="Home")
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

Use the `name` parameter to find elements by their accessible name:

```python
# Find a link by its accessible name (text content)
link = get_by_role(result, "link", name="About")

# Find a button by aria-label
button = get_by_role(result, "button", name="Close dialog")

# Pattern matching with regex
import re

link = get_by_role(result, "link", name=re.compile(r"Home|About"))
```

## Query by Text

Find elements by their text content:

```python
from aria_testing import get_by_text

result = html(t"""
<div>
  <p>Welcome to our site</p>
  <button>Click me</button>
</div>
""")

# Exact match
element = get_by_text(result, "Welcome to our site")

# Pattern matching
import re

element = get_by_text(result, re.compile(r"Welcome.*"))

# Case-insensitive
element = get_by_text(result, "welcome to our site", exact=False)
```

## Query by Label Text

Find form inputs by their associated label:

```python
from aria_testing import get_by_label_text

result = html(t"""
<form>
  <label for="username">Username:</label>
  <input id="username" type="text" />

  <label for="email">Email:</label>
  <input id="email" type="email" />
</form>
""")

username_input = get_by_label_text(result, "Username:")
email_input = get_by_label_text(result, "Email:")
```

## Query by Tag Name

Find elements by their HTML tag name with optional attribute filtering. Useful for testing non-semantic elements like
`<link>`, `<meta>`, `<script>`, etc.

```python
from aria_testing import get_by_tag_name, get_all_by_tag_name

result = html(t"""
<head>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="style.css" />
  <link rel="icon" href="favicon.ico" />
  <link rel="stylesheet" href="theme.css" />
</head>
""")

# Find all stylesheets
stylesheets = get_all_by_tag_name(result, "link", attrs={"rel": "stylesheet"})
assert len(stylesheets) == 2

# Find the favicon
favicon = get_by_tag_name(result, "link", attrs={"rel": "icon"})
assert favicon.attrs["href"] == "favicon.ico"

# Find meta charset
charset = get_by_tag_name(result, "meta", attrs={"charset": "utf-8"})
```

### Special Attribute: `in_class`

Use `in_class` to check if a value is contained in an element's class attribute (substring matching):

```python
result = html(t"""
<div>
  <header class="pico-layout is-fixed-above-lg header-main">Header</header>
  <div class="is-fixed-above-lg sidebar">Sidebar</div>
</div>
""")

# Find header with 'is-fixed-above-lg' in its class
fixed_header = get_by_tag_name(result, "header", attrs={"in_class": "is-fixed-above-lg"})
assert "is-fixed-above-lg" in fixed_header.attrs["class"]

# Combine with other attributes
pico_header = get_by_tag_name(
    result,
    "header",
    attrs={"in_class": "pico-layout"}
)
```

The `in_class` attribute is particularly useful for testing CSS classes that:

- Contain multiple space-separated classes
- Use framework naming conventions (e.g., `btn-primary`, `is-active`)
- Need partial matching rather than exact equality

## Query by Test ID

An escape hatch for when other queries don't work:

```python
from aria_testing import get_by_test_id

result = html(t"""
<div data-testid="custom-element">
  <span>Content</span>
</div>
""")

element = get_by_test_id(result, "custom-element")
```

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

## Query by Class

Find elements by a CSS class token (space-separated values in the `class` attribute). Matching is by exact token, not
substring. There are four variants, consistent with other queries:

- `get_by_class(container, class_name) -> Element`: exactly one match; raises on zero or multiple
- `query_by_class(container, class_name) -> Element | None`: exactly one match; returns `None` on zero, raises on
  multiple
- `get_all_by_class(container, class_name) -> List[Element]`: one or more; raises on zero
- `query_all_by_class(container, class_name) -> List[Element]`: zero or more; never raises

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

# Single element queries
save_button = get_by_class(result, "btn")  # raises if multiple
maybe_title = query_by_class(result, "missing")  # -> None

# Multiple element queries
all_btns = query_all_by_class(result, "btn")  # [<button ...>, <p ...>]
only_btns = get_all_by_class(result, "btn")  # raises if none found

# Token matching, not substring: 'btn' does not match 'button'
assert query_by_class(result, "button").attrs["class"] == "button other"
```

Note: This differs from using `in_class` in tag-name queries, which does substring matching within the class attribute.
Class queries require exact token matches.

## Utility Functions

### get_text_content

Extract all text content from an element:

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

Normalize whitespace in text:

```python
from aria_testing import normalize_text

text = normalize_text("  Hello   World  ")  # "Hello World"
```

## Examples

### Testing a Navigation Component

```python
from tdom import html
from aria_testing import get_by_role, get_all_by_role


def test_navigation():
    nav = html(t"""
    <nav aria-label="Main navigation">
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/docs">Docs</a></li>
        <li><a href="/blog">Blog</a></li>
      </ul>
    </nav>
    """)

    # Find the nav landmark
    navigation = get_by_role(nav, "navigation")
    assert navigation.attrs["aria-label"] == "Main navigation"

    # Find all links
    links = get_all_by_role(nav, "link")
    assert len(links) == 3

    # Find specific link by name
    docs_link = get_by_role(nav, "link", name="Docs")
    assert docs_link.attrs["href"] == "/docs"
```

### Testing a Form

```python
from aria_testing import get_by_label_text, get_by_role


def test_login_form():
    form = html(t"""
    <form>
      <label for="user">Username:</label>
      <input id="user" type="text" />

      <label for="pass">Password:</label>
      <input id="pass" type="password" />

      <button type="submit">Log in</button>
    </form>
    """)

    # Find inputs by label
    username = get_by_label_text(form, "Username:")
    assert username.attrs["type"] == "text"

    password = get_by_label_text(form, "Password:")
    assert password.attrs["type"] == "password"

    # Find submit button
    submit = get_by_role(form, "button", name="Log in")
    assert submit.attrs["type"] == "submit"
```

### Testing a HeaderLink Component

```python
from tdom import Element
from aria_testing import get_by_role
from tdom_sphinx.components.header_link import HeaderLink


def test_header_link():
    svg = '<svg class="icon-github"><path d="..."/></svg>'
    result = HeaderLink(
        href="https://github.com/user/repo",
        aria_label="GitHub repository",
        svg_content=svg,
    )

    assert isinstance(result, Element)

    # Find link by its accessible name
    link = get_by_role(result, "link")
    assert link.attrs["href"] == "https://github.com/user/repo"
    assert link.attrs["aria-label"] == "GitHub repository"
    assert link.attrs["target"] == "_blank"
```

### Testing HTML Head Elements

```python
from aria_testing import get_by_tag_name, get_all_by_tag_name


def test_head_section():
    head = html(t"""
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>My Page</title>
      <link rel="stylesheet" href="_static/sphinx.css" />
      <link rel="stylesheet" href="_static/pygments.css" />
      <link rel="icon" href="_static/favicon.ico" type="image/x-icon" />
    </head>
    """)

    # Find all stylesheets
    stylesheets = get_all_by_tag_name(head, "link", attrs={"rel": "stylesheet"})
    assert len(stylesheets) == 2
    assert stylesheets[0].attrs["href"] == "_static/sphinx.css"

    # Find the favicon
    favicon = get_by_tag_name(head, "link", attrs={"rel": "icon"})
    assert favicon.attrs["href"] == "_static/favicon.ico"
    assert favicon.attrs["type"] == "image/x-icon"

    # Find viewport meta tag
    viewport = get_by_tag_name(head, "meta", attrs={"name": "viewport"})
    assert viewport.attrs["content"] == "width=device-width, initial-scale=1"
```

### Testing Elements with CSS Classes

```python
from aria_testing import get_by_tag_name, query_all_by_tag_name


def test_fixed_layout_elements():
    page = html(t"""
    <body>
      <header class="pico-layout is-fixed-above-lg header-main">
        <nav>Navigation</nav>
      </header>
      <main class="container">
        <div class="is-fixed-above-lg sidebar">Sidebar</div>
      </main>
    </body>
    """)

    # Find header with specific class
    fixed_header = get_by_tag_name(
        page,
        "header",
        attrs={"in_class": "is-fixed-above-lg"}
    )
    assert "pico-layout" in fixed_header.attrs["class"]

    # Find all elements with a specific class (must check each tag type)
    fixed_divs = query_all_by_tag_name(
        page,
        "div",
        attrs={"in_class": "is-fixed-above-lg"}
    )
    assert len(fixed_divs) == 1
    assert "sidebar" in fixed_divs[0].attrs["class"]
```

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

## Best Practices

1. **Prefer queries by role and accessible name** - They match how users interact with your app
2. **Use `get_by_*` in tests** - They fail fast if elements aren't found
3. **Use `query_by_*` for conditional checks** - When testing element absence
4. **Avoid test IDs when possible** - They're implementation details, not user-facing
5. **Test accessibility** - If you can't query it by role/label, users with assistive tech can't use it

## API Reference

### Query Functions

All query functions accept a `container` (Element, Fragment, or Node) and return matching elements.

#### By Role

```python
get_by_role(container, role, name=None) -> Element
query_by_role(container, role, name=None) -> Element | None
get_all_by_role(container, role, name=None) -> List[Element]
query_all_by_role(container, role, name=None) -> List[Element]
```

#### By Text

```python
get_by_text(container, text, exact=True) -> Element
query_by_text(container, text, exact=True) -> Element | None
get_all_by_text(container, text, exact=True) -> List[Element]
query_all_by_text(container, text, exact=True) -> List[Element]
```

#### By Label Text

```python
get_by_label_text(container, text, exact=True) -> Element
query_by_label_text(container, text, exact=True) -> Element | None
get_all_by_label_text(container, text, exact=True) -> List[Element]
query_all_by_label_text(container, text, exact=True) -> List[Element]
```

#### By Tag Name

```python
get_by_tag_name(container, tag, *, attrs=None) -> Element
query_by_tag_name(container, tag, *, attrs=None) -> Element | None
get_all_by_tag_name(container, tag, *, attrs=None) -> List[Element]
query_all_by_tag_name(container, tag, *, attrs=None) -> List[Element]
```

**Parameters:**

- `tag`: HTML tag name (case-insensitive)
- `attrs`: Optional dictionary of attribute name/value pairs
    - Regular attributes use exact matching
    - Special attribute `"in_class"` uses substring matching on the class attribute

#### By Test ID

```python
get_by_test_id(container, test_id) -> Element
query_by_test_id(container, test_id) -> Element | None
get_all_by_test_id(container, test_id) -> List[Element]
query_all_by_test_id(container, test_id) -> List[Element]
```

## See Also

- [DOM Testing Library](https://testing-library.com/docs/dom-testing-library/intro) - Inspiration for this library
- [WAI-ARIA Roles](https://www.w3.org/TR/wai-aria-1.1/#role_definitions) - Complete ARIA role reference
