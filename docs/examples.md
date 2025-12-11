# Examples

This page demonstrates real-world usage patterns for testing components with aria-testing.

## Testing a Navigation Component

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

## Testing a Form

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

## Testing Nested Labels

```python
from aria_testing import get_by_label_text


def test_nested_label():
    form = html(t"""
    <form>
      <label>
        Email Address
        <input type="email" name="email" />
      </label>
    </form>
    """)

    # Label wraps the input - no 'for' attribute needed
    email_input = get_by_label_text(form, "Email Address")
    assert email_input.attrs["type"] == "email"
    assert email_input.attrs["name"] == "email"
```

## Testing a Header Component

```python
from tdom import Element
from aria_testing import get_by_role


def test_header_link():
    # Test a component with SVG content
    svg = '<svg class="icon-github"><path d="..."/></svg>'

    result = html(t"""
    <a href="https://github.com/user/repo"
       aria-label="GitHub repository"
       target="_blank">
      {svg}
    </a>
    """)

    assert isinstance(result, Element)

    # Find link by its accessible name (aria-label)
    link = get_by_role(result, "link")
    assert link.attrs["href"] == "https://github.com/user/repo"
    assert link.attrs["aria-label"] == "GitHub repository"
    assert link.attrs["target"] == "_blank"
```

## Testing HTML Head Elements

Non-semantic elements like `<meta>` and `<link>` don't have ARIA roles, so use tag name queries:

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

## Testing Elements with CSS Classes

### Using Class Queries

```python
from aria_testing import query_all_by_class, get_by_class


def test_button_classes():
    page = html(t"""
    <div>
      <button class="btn primary">Save</button>
      <button class="btn secondary">Cancel</button>
      <button class="btn danger">Delete</button>
    </div>
    """)

    # Find all buttons with 'btn' class
    buttons = query_all_by_class(page, "btn")
    assert len(buttons) == 3

    # Find button with unique class
    primary = get_by_class(page, "primary")
    assert primary.text_content == "Save"
```

### Using Tag Queries with `in_class`

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

    # Find header with specific class substring
    fixed_header = get_by_tag_name(
        page,
        "header",
        attrs={"in_class": "is-fixed-above-lg"}
    )
    assert "pico-layout" in fixed_header.attrs["class"]

    # Find all divs with a specific class substring
    fixed_divs = query_all_by_tag_name(
        page,
        "div",
        attrs={"in_class": "is-fixed-above-lg"}
    )
    assert len(fixed_divs) == 1
    assert "sidebar" in fixed_divs[0].attrs["class"]
```

## Testing Complex Role Hierarchies

```python
from aria_testing import get_by_role, get_all_by_role


def test_document_structure():
    document = html(t"""
    <article>
      <h1>Article Title</h1>
      <h2>Section 1</h2>
      <p>Content here...</p>
      <h2>Section 2</h2>
      <p>More content...</p>
    </article>
    """)

    # Find the article
    article = get_by_role(document, "article")

    # Find the main heading
    title = get_by_role(document, "heading", level=1)
    assert "Article Title" in get_text_content(title)

    # Find all level-2 headings
    sections = get_all_by_role(document, "heading", level=2)
    assert len(sections) == 2
```

## Testing Tables

```python
from aria_testing import get_by_role, get_all_by_role


def test_data_table():
    table = html(t"""
    <table>
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Age</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Alice</td>
          <td>30</td>
        </tr>
        <tr>
          <td>Bob</td>
          <td>25</td>
        </tr>
      </tbody>
    </table>
    """)

    # Find the table
    data_table = get_by_role(table, "table")

    # Find all column headers
    headers = get_all_by_role(table, "columnheader")
    assert len(headers) == 2

    # Find all rows (includes header row)
    rows = get_all_by_role(table, "row")
    assert len(rows) == 3  # 1 header + 2 data rows
```

## Testing with Pattern Matching

```python
import re
from aria_testing import get_by_role, get_by_text


def test_pattern_matching():
    page = html(t"""
    <nav>
      <a href="/home">Home Page</a>
      <a href="/about">About Us</a>
      <a href="/contact">Contact Form</a>
    </nav>
    """)

    # Match links by pattern
    home_link = get_by_role(page, "link", name=re.compile(r"Home"))
    assert home_link.attrs["href"] == "/home"

    # Case-insensitive text matching
    about = get_by_text(page, "about us", exact=False)
    assert about.tag == "a"
```

## Testing for Element Absence

```python
from aria_testing import query_by_role, query_by_text


def test_conditional_rendering():
    # Test when element doesn't exist
    page = html(t"""
    <div>
      <p>Welcome, Guest</p>
    </div>
    """)

    # query_by_* returns None when not found
    logout_button = query_by_role(page, "button", name="Logout")
    assert logout_button is None

    # Check for presence of guest message
    guest_message = query_by_text(page, "Welcome, Guest")
    assert guest_message is not None
```

## Testing Multiple Elements

```python
from aria_testing import get_all_by_role, query_all_by_text


def test_multiple_buttons():
    form = html(t"""
    <form>
      <button type="submit">Submit</button>
      <button type="button">Preview</button>
      <button type="reset">Reset</button>
    </form>
    """)

    # Get all buttons
    buttons = get_all_by_role(form, "button")
    assert len(buttons) == 3

    # Filter by type attribute
    submit_buttons = [
        btn for btn in buttons
        if btn.attrs.get("type") == "submit"
    ]
    assert len(submit_buttons) == 1
```

## Testing Accessible Names from aria-label

```python
from aria_testing import get_by_role


def test_aria_label():
    page = html(t"""
    <nav>
      <button aria-label="Open menu">
        <svg>...</svg>
      </button>
      <button aria-label="Close menu" style="display: none">
        <svg>...</svg>
      </button>
    </nav>
    """)

    # Find buttons by their aria-label
    open_button = get_by_role(page, "button", name="Open menu")
    close_button = get_by_role(page, "button", name="Close menu")

    assert open_button is not None
    assert close_button is not None
```
