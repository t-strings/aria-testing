# aria-testing

Accessibility-focused DOM testing library for tdom.

## Overview

`aria-testing` is a Python DOM testing library that provides accessibility-focused query functions for tdom. It follows
the DOM Testing Library philosophy: **"The more your tests resemble the way your software is used, the more confidence
they can give you."**

## Installation

```bash
uv add --dev aria-testing
```

## Quick Start

```python
from tdom.processor import html
from aria_testing import get_by_role, get_by_text

# Create a tdom structure
document = html(t"""<div>
    <h1>Welcome</h1>
    <nav>
        <a href="/home">Home</a>
    </nav>
    <button>Click me</button>
</div>""")

# Find elements using accessibility patterns
heading = get_by_role(document, "heading", level=1)
nav = get_by_role(document, "navigation")
button = get_by_text(document, "Click me")
link = get_by_role(document, "link", name="Home")
```

## Query Types

- **By Role**: Find elements by their ARIA role (most recommended)
- **By Text**: Find elements by their text content
- **By Label Text**: Find form elements by their associated label
- **By Tag Name**: Find elements by HTML tag name
- **By Test ID**: Find elements by `data-testid` attribute
- **By ID**: Find elements by their HTML `id` attribute
- **By Class**: Find elements by CSS class token

## Query Variants

Each query comes in four variants:

1. **`get_by_*`**: Returns a single element, throws if zero or multiple found
2. **`query_by_*`**: Returns a single element or None, throws if multiple found
3. **`get_all_by_*`**: Returns a list of elements, throws if none found
4. **`query_all_by_*`**: Returns a list of elements (possibly empty)

## Requirements

- Python 3.14+
- tdom

## Documentation

For full documentation, see the [aria-testing guide](docs/aria-testing.md).

## License

MIT
