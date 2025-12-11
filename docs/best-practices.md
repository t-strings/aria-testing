# Best Practices

Guidelines for writing effective, maintainable tests with aria-testing.

## Query Priority

Use queries in this order of preference:

### 1. **By Role** ⭐⭐⭐ (Highest Priority)

Find elements by their ARIA role - mirrors how screen readers interact with your app.

```python
button = get_by_role(document, "button")
heading = get_by_role(document, "heading", level=1)
link = get_by_role(document, "link", name="Home")
```

**Why prioritize role queries?**
- Tests how users with assistive technology experience your app
- Encourages semantic HTML
- Resilient to implementation changes (CSS classes, IDs, structure)
- Forces you to think about accessibility

### 2. **By Label Text** ⭐⭐⭐

Find form elements by their associated label - how users identify form fields.

```python
username = get_by_label_text(document, "Username")
email = get_by_label_text(document, "Email Address")
```

**Why prioritize label queries?**
- Matches how users identify form inputs
- Ensures labels are properly associated
- Tests accessibility of forms
- Resilient to implementation changes

### 3. **By Text** ⭐⭐

Find elements by their text content.

```python
button = get_by_text(document, "Click me")
heading = get_by_text(document, "Welcome")
```

**Why lower priority than role?**
- Text can change more frequently than roles
- Doesn't verify semantic structure
- Less specific than role + name combination

**When to use:**
- Content verification (headings, paragraphs)
- When role queries aren't specific enough
- Testing displayed text

### 4. **By Test ID** ⭐

Find elements by `data-testid` attribute - escape hatch when semantic queries fail.

```python
component = get_by_test_id(document, "user-menu")
```

**Why lowest priority?**
- Implementation detail, not user-facing
- Adds attributes solely for testing
- Doesn't encourage accessibility
- Doesn't match how users interact

**When to use:**
- Complex components without clear roles
- Dynamic content with changing text
- When semantic queries are impractical
- Testing implementation-specific behavior

### 5. **By Tag Name, ID, Class**

Direct attribute queries - use sparingly.

```python
# Tag name: useful for non-semantic elements
favicon = get_by_tag_name(document, "link", attrs={"rel": "icon"})

# ID: when element has unique ID
element = get_by_id(document, "main-content")

# Class: when other queries fail
buttons = get_all_by_class(document, "btn-primary")
```

**When to use:**
- Non-semantic HTML elements (`<link>`, `<meta>`, `<script>`)
- Testing specific HTML structure
- When semantic queries aren't possible

## Query Variant Selection

Choose the right variant for your use case:

### `get_by_*` - Most Common

Use when element **MUST exist** and be **unique**:

```python
# Element is required and unique
button = get_by_role(document, "button", name="Submit")
heading = get_by_text(document, "Welcome")
```

**Fails fast:**
- Raises `ElementNotFoundError` if not found
- Raises `MultipleElementsError` if multiple found

### `query_by_*` - Conditional Checks

Use when checking if element **exists or not**:

```python
# Check for conditional rendering
logout_button = query_by_role(document, "button", name="Logout")
if logout_button is None:
    # User not logged in
    login_link = get_by_role(document, "link", name="Login")
```

**Returns `None` instead of raising** when not found.

### `get_all_by_*` - Multiple Required

Use when multiple elements **MUST exist**:

```python
# Verify multiple items exist
links = get_all_by_role(nav, "link")
assert len(links) == 3
```

**Fails fast:**
- Raises `ElementNotFoundError` if none found
- Returns all matches if any exist

### `query_all_by_*` - Exploratory

Use when finding **zero or more** elements:

```python
# Find all, might be empty
errors = query_all_by_role(form, "alert")
if errors:
    # Handle errors
    pass
```

**Never raises** - returns empty list if none found.

## Accessibility Testing

### Test What Users Experience

```python
# ✅ Good - tests accessible name
button = get_by_role(document, "button", name="Close dialog")

# ❌ Bad - tests implementation detail
button = get_by_test_id(document, "close-btn")
```

### Verify Semantic Structure

```python
# ✅ Good - verifies heading hierarchy
h1 = get_by_role(document, "heading", level=1)
h2 = get_by_role(document, "heading", level=2)

# ❌ Bad - doesn't verify semantic meaning
h1 = get_by_tag_name(document, "h1")
```

### Ensure Form Accessibility

```python
# ✅ Good - verifies label association
email_input = get_by_label_text(form, "Email Address")

# ❌ Bad - doesn't verify label exists
email_input = get_by_tag_name(form, "input", attrs={"name": "email"})
```

### Test Landmark Navigation

```python
# ✅ Good - tests page landmarks
nav = get_by_role(document, "navigation")
main = get_by_role(document, "main")
footer = get_by_role(document, "contentinfo")

# ❌ Bad - doesn't verify landmark roles
nav = get_by_tag_name(document, "nav")
```

## Pattern Matching

Use regex for flexible matching:

```python
import re

# Case-insensitive matching
link = get_by_role(document, "link", name=re.compile(r"home", re.IGNORECASE))

# Partial matching
heading = get_by_text(document, re.compile(r"Welcome.*"))

# Multiple options
button = get_by_role(document, "button", name=re.compile(r"Save|Submit"))
```

## Error Handling

### Let Tests Fail Fast

```python
# ✅ Good - fails immediately with clear error
button = get_by_role(document, "button", name="Submit")

# ❌ Bad - returns None, test fails later with unclear error
button = query_by_role(document, "button", name="Submit")
assert button is not None  # Less clear failure message
```

### Use Descriptive Queries

```python
# ✅ Good - error message includes "Submit"
button = get_by_role(document, "button", name="Submit")

# ❌ Bad - error message just says "button not found"
button = get_by_role(document, "button")
```

### Handle Expected Absences

```python
# ✅ Good - explicit about checking absence
logout = query_by_role(document, "button", name="Logout")
assert logout is None, "Should not show logout when not logged in"

# ❌ Bad - try/except hides the intent
try:
    logout = get_by_role(document, "button", name="Logout")
    assert False, "Should not find logout button"
except ElementNotFoundError:
    pass  # Expected
```

## Performance Tips

### Reuse Containers

Cache benefits from repeated queries on the same container:

```python
# ✅ Good - queries same document, benefits from cache
def test_page():
    document = render_page()

    nav = get_by_role(document, "navigation")
    main = get_by_role(document, "main")
    footer = get_by_role(document, "contentinfo")

# ❌ Less efficient - re-renders between queries
def test_page():
    nav = get_by_role(render_page(), "navigation")
    main = get_by_role(render_page(), "main")  # New document, cold cache
```

### Scope Queries Appropriately

Query from the smallest container that includes your target:

```python
# ✅ Good - scoped to specific section
form = get_by_role(document, "form")
submit = get_by_role(form, "button", name="Submit")  # Only searches form

# ❌ Less efficient - searches entire document
submit = get_by_role(document, "button", name="Submit")
```

### Use `query_all_*` for Multiple Queries

Full caching benefits when finding all matches:

```python
# ✅ Good - single query gets all
links = query_all_by_role(nav, "link")
home_link = next(l for l in links if "Home" in get_text_content(l))

# ❌ Less efficient - multiple queries
home_link = get_by_role(nav, "link", name="Home")
docs_link = get_by_role(nav, "link", name="Docs")
```

## Test Organization

### Group Related Queries

```python
def test_navigation_structure():
    """Test the navigation component structure and accessibility."""
    nav = get_by_role(document, "navigation")

    # Test landmark
    assert nav.attrs["aria-label"] == "Main navigation"

    # Test links
    links = get_all_by_role(nav, "link")
    assert len(links) == 3

    # Test specific links
    home = get_by_role(nav, "link", name="Home")
    assert home.attrs["href"] == "/"
```

### Separate Structure and Content

```python
def test_form_structure():
    """Test form has correct semantic structure."""
    form = get_by_role(document, "form")
    get_by_label_text(form, "Username")
    get_by_label_text(form, "Password")
    get_by_role(form, "button", name="Login")


def test_form_behavior():
    """Test form submission behavior."""
    # Test behavior separately from structure
    pass
```

## Common Pitfalls

### Don't Test Implementation Details

```python
# ❌ Bad - tests CSS classes
buttons = get_all_by_class(document, "btn-primary")

# ✅ Good - tests accessible interface
buttons = get_all_by_role(document, "button")
```

### Don't Over-Specify Queries

```python
# ❌ Bad - overly specific, brittle
button = get_by_tag_name(
    document,
    "button",
    attrs={"class": "btn btn-primary", "id": "submit-btn"}
)

# ✅ Good - specific enough, flexible
button = get_by_role(document, "button", name="Submit")
```

### Don't Mix Query Strategies

```python
# ❌ Bad - inconsistent strategy
nav = get_by_role(document, "navigation")
links = get_all_by_tag_name(nav, "a")  # Why switch to tag name?

# ✅ Good - consistent use of roles
nav = get_by_role(document, "navigation")
links = get_all_by_role(nav, "link")
```

### Don't Ignore Accessibility Failures

```python
# ❌ Bad - falls back to test ID without fixing accessibility
try:
    button = get_by_role(document, "button", name="Submit")
except ElementNotFoundError:
    button = get_by_test_id(document, "submit-btn")  # Hides accessibility issue

# ✅ Good - let test fail, fix the component
button = get_by_role(document, "button", name="Submit")
```

## Testing Non-Semantic Elements

Some elements don't have ARIA roles and should use tag queries:

```python
# ✅ Good - use tag queries for <head> elements
stylesheets = get_all_by_tag_name(head, "link", attrs={"rel": "stylesheet"})
favicon = get_by_tag_name(head, "link", attrs={"rel": "icon"})
viewport = get_by_tag_name(head, "meta", attrs={"name": "viewport"})

# ✅ Good - use tag queries for scripts
scripts = get_all_by_tag_name(document, "script")
```

## Summary Checklist

- [ ] Prefer role queries over other query types
- [ ] Use label queries for form inputs
- [ ] Use `get_by_*` for required unique elements
- [ ] Use `query_by_*` for conditional checks
- [ ] Let tests fail fast with clear error messages
- [ ] Test accessible names and semantic structure
- [ ] Avoid testing implementation details (classes, IDs, structure)
- [ ] Reuse containers to benefit from caching
- [ ] Use descriptive query parameters
- [ ] Handle expected absences explicitly with `query_by_*`

## See Also

- [Query Reference](queries.md) - All available query functions
- [Examples](examples.md) - Real-world testing patterns
- [API Reference](api.md) - Complete function signatures
