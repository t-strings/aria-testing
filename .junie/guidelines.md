# CLAUDE.md

Guidance for Claude Code when working with this tdom-sphinx repository.

## Quick Commands

```bash
uv sync --group dev                            # Install dependencies
uv run pytest                                  # Run all tests
uv run pyright                                 # Type check
uv run ruff format                             # Format code
 uv run sphinx-autobuild docs docs/_build/html # Live docs server
```

## Python notes

- **3.14**. Use all the latest features from recent Python releases, up to the Python 3.14 release:
  - Prefer a type hint with `| None` instead of `Optional`
  - Don't use `from __future__ import annotations`
  - Use forward reference type hints
  - Don't use `getattr` on objects that are dataclasses to fix type hinting, trust the dataclass.

## Architecture

This Sphinx theme uses `tdom` (template DOM) with components instead of Jinja templates:

- **Template Bridge**: `TdomBridge` replaces Sphinx's template loader
- **Models**: `PageContext` (per-page), `SiteConfig` (site-wide)
- **Views**: `DefaultView` orchestrates layout using components
- **Components**: Functional components in `components/` returning tdom `Node`
- **URL Management**: `relative_tree()` rewrites URLs for multi-level sites

## Component Creation Workflow

**IMPORTANT**: When creating or extracting a component, follow ALL these steps:

### 1. Create Component File
- Location: `src/tdom_sphinx/components/`
- Naming: CamelCase function (`HeaderLink`) → snake_case file (`header_link.py`)
- Signature: Always start with `*` to force named parameters
- Return type: `Node`

```python
def HeaderLink(*, href: str, aria_label: str) -> Node:
    return html(t"""<li><a href={href} aria-label={aria_label}>...</a></li>""")
```

### 2. Create Test File
- Location: Same directory as component
- Naming: Add `_test.py` suffix (`header_link_test.py`)
- Pattern: Use `html(t'')` to generate `container`, then query with aria_testing

```python
def test_header_link_renders_basic() -> None:
    container = html(t"""<{HeaderLink} href="/" aria_label="Home" />""")
    assert isinstance(container, Element)  # Fix type checking

    link = get_by_role(container, "link", name="Home")
    assert link.attrs.get("href") == "/"
```

### 3. Run Tests
```bash
uv run pytest src/tdom_sphinx/components/header_link_test.py -v
```

### 4. Quality Checks
```bash
uv run ruff format src/tdom_sphinx/components/header_link.py
uv run pyright src/tdom_sphinx/components/header_link.py
```
Ensure ZERO errors on both.

### 5. Write Documentation
**REQUIRED** - Documentation must be written for all user-facing components.

- Location: `docs/components/component_name.md`
- Format: Markdown/MyST
- Required Sections:
  - **Title and Overview**: Brief description of what the component does
  - **Usage**: Python code example showing basic usage
  - **Parameters**: List all parameters with types and descriptions
  - **Features**: Key features and behaviors
  - **Example Output**: Show the generated HTML
  - **Common Use Cases**: Real-world examples with code
  - **Design Considerations**: Important notes about usage, limitations, integration
- Link: Add to toctree in `docs/components/index.md` if not already there

**Example Documentation Structure** (see `docs/components/header_link.md` or `docs/components/version_picker.md`):
```markdown
# ComponentName

Brief description of the component.

## Overview
Detailed explanation of what it does and when to use it.

## Usage
```python
from tdom_sphinx.components.component_name import ComponentName

result = ComponentName(param1="value", param2=True)
```

## Parameters
- **param1** (type, required): Description
- **param2** (type, optional): Description, defaults to X

## Features
- Feature 1
- Feature 2

## Example Output
```html
<expected>output</expected>
```

## Common Use Cases
### Use Case 1
[Code example]

### Use Case 2
[Code example]

## Design Considerations
- Important notes
- Limitations
- Integration details
```

**Why Documentation is Required:**
- Components are user-facing API - developers need to know how to use them
- Documentation serves as specification for component behavior
- Examples help users understand proper usage patterns
- Design considerations prevent misuse and clarify intent

## Key Guidelines

**t-strings (PEP 750)**:
- Template strings use `t"""..."""` syntax
- Interpolations use `{variable}` or `{expression}`
- Always add type hints on functions

**Testing**:
- Component tests: Use `aria_testing` queries (`get_by_role`, `get_by_text`, etc.)
- Access attributes: `element.attrs.get("href")` not `element.get("href")`
- Type fixes: Add `isinstance(container, Element)` after `html()` calls
- Use pytest functions, not classes

**Components**:
- Use `*` as first parameter to enforce named arguments
- Return `Node` type
- Compose hierarchically (e.g., `Header` → `NavbarBrand` + `NavbarLinks`)
- For raw HTML (like SVG), use `Markup()` from `tdom_sphinx.tdom_safe`

**Code Quality**:
- Remove unused imports
- Run `uv run ruff format` after changes
- Run `uv run pyright` to verify types
- Use `uv run python` for Python execution

**Documentation**:
- **REQUIRED** for all user-facing components (see step 5 of Component Creation Workflow)
- Must include all required sections: Overview, Usage, Parameters, Features, Example Output, Common Use Cases, Design Considerations
- Reference existing docs as examples: `docs/components/header_link.md`, `docs/components/version_picker.md`
- Link into appropriate toctree (typically `docs/components/index.md`)
- Write documentation immediately after component creation - don't defer it

## Testing Strategy

- **Component Tests**: `components/*_test.py` - isolated component functionality
- **Integration Tests**: `tests/test_*.py` - Sphinx integration with fixtures
- **Test Projects**: `tests/roots/` - sample Sphinx projects for testing

**Common Fixtures**:
- `sphinx_app`: SphinxTestApp with SiteConfig
- `page_context`: Sample PageContext
- `site_config`: Sample SiteConfig
- `content`: Built Sphinx app

## Notes

- Python 3.14+ with PEP 750 t-strings
- `tdom` installed as editable from `../tdom`
- URL rewriting via `relative_tree()` after rendering
- Always use pytest function tests, never class-based
