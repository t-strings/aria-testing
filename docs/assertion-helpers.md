# Assertion Helpers

Assertion helpers are frozen dataclass-based wrappers around aria-testing query functions, designed for **deferred execution** in dynamic systems. They allow you to define assertions declaratively *before* the DOM is available, then apply them later when the container becomes available.

## The Problem They Solve

In dynamic testing systems—component testing frameworks, story-based testing, test fixtures—you often need to:

1. **Define assertions early**, before the DOM exists
2. **Execute assertions later**, when the container becomes available
3. **Reuse assertions** across multiple test scenarios
4. **Compose complex assertions** from simpler building blocks

Traditional imperative assertions don't support this pattern:

```python
# ❌ Imperative - requires immediate DOM access
def test_button():
    container = render_component()
    button = get_by_role(container, "button")
    assert get_text_content(button) == "Save"
    assert button.attrs["type"] == "submit"
```

Assertion helpers enable declarative, deferred execution:

```python
# ✅ Declarative - define assertion before DOM exists
assert_save_button = (
    GetByRole(role="button")
    .text_content("Save")
    .with_attribute("type", "submit")
)

# Apply later when container is available
def test_button():
    container = render_component()
    assert_save_button(container)  # Raises AssertionError if fails
```

## Core Concept: Frozen Dataclasses with `__call__`

Each helper is a **frozen dataclass** that stores query parameters and assertion conditions. The `__call__` method executes the assertion against a container:

```python
from aria_testing import GetByRole

# Create helper instance (frozen dataclass)
helper = GetByRole(role="button")

# Later: call it with a container
helper(container)  # Executes query, raises AssertionError if not found
```

**Key characteristics:**

- **Immutable** - Frozen dataclasses prevent accidental modification
- **Callable** - Accepts `Element | Fragment | Node` via `__call__`
- **Composable** - Fluent API returns new instances
- **Type-safe** - Full type hints with IDE support

## Basic Usage

### Single Element Assertions

```python
from tdom import html
from aria_testing import (
    GetByRole,
    GetByText,
    GetByLabelText,
    GetByTestId,
    GetByClass,
    GetById,
    GetByTagName,
)

container = html(t'<div><button type="submit">Save</button></div>')

# Assert element exists
GetByRole(role="button")(container)
GetByText(text="Save")(container)
GetByTagName(tag_name="button")(container)

# All raise AssertionError if element not found
```

### With Role Parameters

```python
# Heading with level
GetByRole(role="heading", level=1)(container)

# Button with accessible name
GetByRole(role="button", name="Submit")(container)
```

## Fluent API: Building Complex Assertions

Assertion helpers support method chaining to build complex assertions. Each method returns a **new instance** (immutability preserved).

### Negation: `.not_()`

Assert that an element does **not** exist:

```python
# Assert no modal dialog is present
GetByRole(role="dialog").not_()(container)

# Assert button is not in the DOM
GetByText(text="Delete").not_()(container)
```

### Text Content: `.text_content(expected)`

Verify element's text content matches expected value:

```python
# Button must have specific text
GetByRole(role="button").text_content("Save Changes")(container)

# Heading must have title text
GetByRole(role="heading", level=1).text_content("Welcome")(container)
```

### Attribute Checks: `.with_attribute(name, value=None)`

Verify element has specific attributes:

```python
# Check attribute value
GetByRole(role="button").with_attribute("type", "submit")(container)

# Check attribute exists (any value)
GetByRole(role="button").with_attribute("disabled")(container)

# Chain multiple attribute checks
GetByRole(role="button").with_attribute("type", "submit").with_attribute("aria-label", "Save")(container)
```

### Method Chaining

Combine multiple modifiers:

```python
# Complex assertion
assert_submit_button = (
    GetByRole(role="button")
    .text_content("Submit")
    .with_attribute("type", "submit")
    .with_attribute("aria-label", "Submit form")
)

# Apply to any container
assert_submit_button(container1)
assert_submit_button(container2)
```

## List Assertions: `GetAllBy*` Helpers

For multiple elements, use `GetAllBy*` variants with count and selection operations.

### Available List Helpers

```python
from aria_testing import (
    GetAllByRole,
    GetAllByText,
    GetAllByLabelText,
    GetAllByTestId,
    GetAllByClass,
    GetAllByTagName,
)
```

### Count Assertions: `.count(expected)`

Verify exact number of matching elements:

```python
container = html(t'''
<ul>
    <li>Item 1</li>
    <li>Item 2</li>
    <li>Item 3</li>
</ul>
''')

# Assert exactly 3 list items
GetAllByRole(role="listitem").count(3)(container)

# Assert 5 buttons total
GetAllByTagName(tag_name="button").count(5)(container)
```

**Error message on failure:**

```
AssertionError: Expected count: 3 but found: 5 elements

Query: role='listitem'
```

### Item Selection: `.nth(index)`

Select a specific element from the list (zero-indexed):

```python
container = html(t'''
<div>
    <button>First</button>
    <button>Second</button>
    <button>Third</button>
</div>
''')

# Assert first button has specific text
GetAllByRole(role="button").nth(0).text_content("First")(container)

# Assert third button is disabled
GetAllByRole(role="button").nth(2).with_attribute("disabled")(container)
```

### Combining Count and Selection

```python
# Assert exactly 3 buttons, and verify the second one
assert_buttons = (
    GetAllByRole(role="button")
    .count(3)
    .nth(1)
    .text_content("Middle Button")
)

assert_buttons(container)
```

### Out of Bounds Handling

```python
# Only 2 buttons, but requesting index 5
GetAllByRole(role="button").nth(5)(container)

# AssertionError: Index 5 out of bounds, found 2 elements
```

## Use Cases

### 1. Component Testing Frameworks

Define reusable assertions for component verification:

```python
# Define assertion set for a card component
class CardAssertions:
    title = GetByRole(role="heading", level=2)
    description = GetByRole(role="paragraph")
    action_button = GetByRole(role="button").text_content("Learn More")

def test_card_component():
    container = render_card(title="Product", description="...", action="Learn More")

    CardAssertions.title(container)
    CardAssertions.description(container)
    CardAssertions.action_button(container)
```

### 2. Story-Based Testing

Separate assertion definition from execution:

```python
from dataclasses import dataclass

@dataclass
class Story:
    name: str
    render: Callable[[], Node]
    assertions: list[Callable[[Node], None]]

# Define stories with assertions
button_story = Story(
    name="Primary Button",
    render=lambda: render_button(variant="primary"),
    assertions=[
        GetByRole(role="button").with_attribute("class", "btn-primary"),
        GetByRole(role="button").text_content("Click Me"),
    ]
)

# Execute story later
def test_story(story: Story):
    container = story.render()
    for assertion in story.assertions:
        assertion(container)  # Apply each assertion
```

### 3. Test Fixtures with Deferred Verification

Set up fixtures with pre-defined assertions:

```python
import pytest

@pytest.fixture
def form_assertions():
    """Reusable form assertions."""
    return {
        "username": GetByLabelText(label="Username").with_attribute("type", "text"),
        "password": GetByLabelText(label="Password").with_attribute("type", "password"),
        "submit": GetByRole(role="button", name="Submit"),
    }

def test_login_form(form_assertions):
    container = render_login_form()

    # Apply all assertions
    form_assertions["username"](container)
    form_assertions["password"](container)
    form_assertions["submit"](container)
```

### 4. Parameterized Testing

Reuse assertions across different inputs:

```python
import pytest

# Define assertion once
assert_heading = GetByRole(role="heading", level=1)

@pytest.mark.parametrize("page", ["home", "about", "contact"])
def test_page_has_heading(page):
    container = render_page(page)
    assert_heading(container)  # Same assertion, different containers
```

### 5. Assertion Composition

Build complex assertions from simpler ones:

```python
# Base assertions
has_button = GetByRole(role="button")
has_submit_button = has_button.with_attribute("type", "submit")
has_submit_with_text = has_submit_button.text_content("Submit Form")

# Progressive refinement
def test_form():
    container = render_form()

    # Start simple, add constraints
    has_button(container)  # Any button
    has_submit_button(container)  # Submit button specifically
    has_submit_with_text(container)  # With exact text
```

## Error Messages

Assertion helpers provide detailed error messages on failure:

```python
GetByRole(role="button").text_content("Save")(container)
```

**Error output:**

```
AssertionError: Unable to find element with role 'button'

Query: role='button'

Searched in:
<div class="container">
  <span>No buttons here</span>
</div>
```

**Text mismatch:**

```
AssertionError: Expected text: 'Save' but got: 'Cancel'

Query: role='button'
```

**Attribute errors:**

```
AssertionError: Expected attribute 'type'='submit' but got 'button'

Query: role='button'
```

## Complete Reference

### Single Element Helpers

| Helper | Parameters | Description |
|--------|-----------|-------------|
| `GetByRole` | `role`, `level=None`, `name=None` | Find by ARIA role |
| `GetByText` | `text` | Find by text content |
| `GetByLabelText` | `label` | Find by label text |
| `GetByTestId` | `test_id` | Find by data-testid |
| `GetByClass` | `class_name` | Find by CSS class |
| `GetById` | `id` | Find by ID attribute |
| `GetByTagName` | `tag_name` | Find by HTML tag |

### List Helpers (with `.count()` and `.nth()`)

| Helper | Parameters | Description |
|--------|-----------|-------------|
| `GetAllByRole` | `role`, `level=None`, `name=None` | Find all by ARIA role |
| `GetAllByText` | `text` | Find all by text content |
| `GetAllByLabelText` | `label` | Find all by label text |
| `GetAllByTestId` | `test_id` | Find all by data-testid |
| `GetAllByClass` | `class_name` | Find all by CSS class |
| `GetAllByTagName` | `tag_name` | Find all by HTML tag |

### Fluent API Methods

| Method | Applies To | Description |
|--------|-----------|-------------|
| `.not_()` | All helpers | Assert element does NOT exist |
| `.text_content(expected)` | All helpers | Verify element's text content |
| `.with_attribute(name, value=None)` | All helpers | Verify attribute exists/matches |
| `.count(expected)` | `GetAllBy*` only | Verify number of elements |
| `.nth(index)` | `GetAllBy*` only | Select specific element (0-indexed) |

## Implementation Details

### Type Signature

All helpers accept `Container` which is defined as:

```python
Container = Element | Fragment | Node
```

This allows passing any tdom structure returned by `html()`.

### Immutability

Helpers are frozen dataclasses—all fluent methods return **new instances**:

```python
original = GetByRole(role="button")
modified = original.not_()

assert original.negate is False  # Original unchanged
assert modified.negate is True   # New instance created
```

### Execution Flow

When calling a helper:

1. Execute underlying aria-testing query function
2. If `.not_()` used:
   - Element found → raise AssertionError
   - Element not found → success (no error)
3. Otherwise:
   - Element not found → raise AssertionError
   - Element found → check modifiers (text, attributes)
4. Apply `.text_content()` verification if specified
5. Apply `.with_attribute()` checks if specified
6. For `GetAllBy*` with `.nth()`:
   - Verify index is in bounds
   - Select element at index
   - Apply text/attribute checks to selected element

## Best Practices

### ✅ Do

- **Define assertions once, reuse multiple times**
- **Use descriptive variable names** (`assert_submit_button` not `helper`)
- **Combine with test fixtures** for reusable assertion sets
- **Use `.not_()` for absence assertions** rather than wrapping in try/except
- **Prefer semantic queries** (`GetByRole`, `GetByLabelText`) over test IDs

### ❌ Don't

- **Don't mutate helpers** (they're frozen—won't work anyway)
- **Don't catch AssertionError** to implement custom logic (defeats the purpose)
- **Don't create one-off helpers** for simple direct queries (just use the query functions)
- **Don't over-chain** modifiers when separate assertions would be clearer

## Migration from Direct Queries

**Before (imperative):**

```python
def test_form():
    container = render_form()
    button = get_by_role(container, "button")
    assert get_text_content(button) == "Submit"
    assert button.attrs["type"] == "submit"
```

**After (declarative):**

```python
assert_submit = (
    GetByRole(role="button")
    .text_content("Submit")
    .with_attribute("type", "submit")
)

def test_form():
    container = render_form()
    assert_submit(container)
```

## See Also

- **[Query Reference](queries.md)** - Underlying query functions
- **[Examples](examples.md)** - More usage examples
- **[API Reference](api.md)** - Complete API documentation
