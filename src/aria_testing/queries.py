"""
Query functions for finding elements in tdom trees using accessibility patterns.

All query functions accept both Element and Fragment containers, allowing you to
search within any tdom structure returned by html().
"""

import re
import sys
from types import MappingProxyType
from typing import Callable, Literal

from tdom import Element, Fragment, Node

from aria_testing.errors import ElementNotFoundError, MultipleElementsError
from aria_testing.utils import (
    find_elements_by_attribute,
    get_accessible_name,
    get_all_elements,
    get_text_content,
)

# Type alias for containers that can be searched
# Accepts both Element, Fragment, and Node as valid containers
Container = Element | Fragment | Node

# ARIA Role Type Definition
# Based on WAI-ARIA 1.1 specification and HTML living standard
# Simplified to a single flat Literal for easier maintenance
AriaRole = Literal[
    # Landmark roles - Define page structure and navigation
    "banner",
    "complementary",
    "contentinfo",
    "form",
    "main",
    "navigation",
    "region",
    "search",
    # Document structure roles - Organize content
    "article",
    "document",
    "feed",
    "figure",
    "img",
    "list",
    "listitem",
    "math",
    "none",
    "presentation",
    "table",
    "rowgroup",
    "row",
    "cell",
    "columnheader",
    "rowheader",
    "gridcell",
    "heading",
    "separator",
    # Widget roles - Interactive elements
    "button",
    "checkbox",
    "link",
    "menuitem",
    "menuitemcheckbox",
    "menuitemradio",
    "option",
    "progressbar",
    "radio",
    "scrollbar",
    "searchbox",
    "slider",
    "spinbutton",
    "switch",
    "tab",
    "tabpanel",
    "textbox",
    "treeitem",
    # Composite widget roles - Complex interactive elements
    "combobox",
    "grid",
    "listbox",
    "menu",
    "menubar",
    "radiogroup",
    "tablist",
    "tree",
    "treegrid",
    # Live region roles - Dynamic content
    "alert",
    "log",
    "marquee",
    "status",
    "timer",
    # Window roles - Application-like interfaces
    "alertdialog",
    "dialog",
]

# Keep individual role categories for internal use if needed
LandmarkRole = Literal[
    "banner",
    "complementary",
    "contentinfo",
    "form",
    "main",
    "navigation",
    "region",
    "search",
]
DocumentStructureRole = Literal[
    "article",
    "document",
    "feed",
    "figure",
    "img",
    "list",
    "listitem",
    "math",
    "none",
    "presentation",
    "table",
    "rowgroup",
    "row",
    "cell",
    "columnheader",
    "rowheader",
    "gridcell",
    "heading",
    "separator",
]
WidgetRole = Literal[
    "button",
    "checkbox",
    "gridcell",
    "link",
    "menuitem",
    "menuitemcheckbox",
    "menuitemradio",
    "option",
    "progressbar",
    "radio",
    "scrollbar",
    "searchbox",
    "slider",
    "spinbutton",
    "switch",
    "tab",
    "tabpanel",
    "textbox",
    "treeitem",
]
CompositeWidgetRole = Literal[
    "combobox",
    "grid",
    "listbox",
    "menu",
    "menubar",
    "radiogroup",
    "tablist",
    "tree",
    "treegrid",
]
LiveRegionRole = Literal["alert", "log", "marquee", "status", "timer"]
WindowRole = Literal["alertdialog", "dialog"]

# Note: Using keyword-only arguments with * separator instead of options dictionary

# Error message templates for consistency
_NOT_FOUND_MSG = "Unable to find element with {query_type}: {value}"
_NOT_FOUND_PLURAL_MSG = "Unable to find elements with {query_type}: {value}"
_MULTIPLE_MSG = "Found multiple elements with {query_type}: {value}"


# Generic query wrapper factory - reduces boilerplate
def _make_query_variants(
    query_all_func: Callable[..., list[Element]],
    query_type: str,
) -> tuple[
    Callable[..., list[Element]],
    Callable[..., Element | None],
    Callable[..., Element],
    Callable[..., list[Element]],
]:
    """
    Generate query/get/get_all variants from a query_all base function.

    This factory creates four query functions from a single implementation:
    - query_all_by_*: Returns list (possibly empty)
    - query_by_*: Returns first element or None
    - get_by_*: Returns first element or raises error
    - get_all_by_*: Returns list or raises error

    Args:
        query_all_func: Base function that returns list[Element]
        query_type: Human-readable name for error messages (e.g., "text", "role")

    Returns:
        Tuple of (query_all, query_by, get_by, get_all) functions
    """

    def query_by(*args, **kwargs) -> Element | None:
        """Return first matching element or None (raises on multiple matches)."""
        # Early exit optimization: only need to find 2 elements max
        kwargs_with_limit = {**kwargs, "_max_results": 2}
        elements = query_all_func(*args, **kwargs_with_limit)
        if not elements:
            return None
        if len(elements) > 1:
            value_str = str(args[1]) if len(args) > 1 else "..."
            raise MultipleElementsError(
                _MULTIPLE_MSG.format(query_type=query_type, value=value_str),
                count=len(elements),
            )
        return elements[0]

    def get_by(*args, **kwargs) -> Element:
        """Return first matching element or raise error."""
        # Early exit optimization: only need to find 2 elements max
        kwargs_with_limit = {**kwargs, "_max_results": 2}
        elements = query_all_func(*args, **kwargs_with_limit)
        if not elements:
            # Try to extract meaningful value from args for error message
            value_str = str(args[1]) if len(args) > 1 else "..."
            raise ElementNotFoundError(
                _NOT_FOUND_MSG.format(query_type=query_type, value=value_str)
            )
        if len(elements) > 1:
            value_str = str(args[1]) if len(args) > 1 else "..."
            raise MultipleElementsError(
                _MULTIPLE_MSG.format(query_type=query_type, value=value_str),
                count=len(elements),
            )
        return elements[0]

    def get_all(*args, **kwargs) -> list[Element]:
        """Return all matching elements or raise error."""
        elements = query_all_func(*args, **kwargs)
        if not elements:
            value_str = str(args[1]) if len(args) > 1 else "..."
            raise ElementNotFoundError(
                _NOT_FOUND_PLURAL_MSG.format(query_type=query_type, value=value_str)
            )
        return elements

    # Preserve function names for debugging
    query_by.__name__ = f"query_by_{query_type}"
    get_by.__name__ = f"get_by_{query_type}"
    get_all.__name__ = f"get_all_by_{query_type}"

    return query_all_func, query_by, get_by, get_all


# Immutable role mappings for performance with string interning
# String interning makes string comparisons faster via identity check
# MappingProxyType enforces immutability at runtime
_ROLE_MAP = MappingProxyType(
    {
        sys.intern("button"): sys.intern("button"),
        sys.intern("summary"): sys.intern(
            "button"
        ),  # <summary> has implicit role of button
        sys.intern("nav"): sys.intern("navigation"),
        sys.intern("main"): sys.intern("main"),
        sys.intern("header"): sys.intern("banner"),
        sys.intern("footer"): sys.intern("contentinfo"),
        sys.intern("aside"): sys.intern("complementary"),
        sys.intern("h1"): sys.intern("heading"),
        sys.intern("h2"): sys.intern("heading"),
        sys.intern("h3"): sys.intern("heading"),
        sys.intern("h4"): sys.intern("heading"),
        sys.intern("h5"): sys.intern("heading"),
        sys.intern("h6"): sys.intern("heading"),
        sys.intern("a"): sys.intern("link"),
        sys.intern("ul"): sys.intern("list"),
        sys.intern("ol"): sys.intern("list"),
        sys.intern("li"): sys.intern("listitem"),
        sys.intern("form"): sys.intern("form"),
        sys.intern("img"): sys.intern("img"),
        sys.intern("textarea"): sys.intern("textbox"),
    }
)

_INPUT_TYPE_MAP = MappingProxyType(
    {
        sys.intern("text"): sys.intern("textbox"),
        sys.intern("email"): sys.intern("textbox"),
        sys.intern("password"): sys.intern("textbox"),
        sys.intern("number"): sys.intern("spinbutton"),
        sys.intern("checkbox"): sys.intern("checkbox"),
        sys.intern("radio"): sys.intern("radio"),
        sys.intern("button"): sys.intern("button"),
        sys.intern("submit"): sys.intern("button"),
        sys.intern("reset"): sys.intern("button"),
    }
)


def get_role_for_element(node: Node) -> str | None:
    """
    Get the ARIA role for a node (only Elements can have roles).
    """
    # Only Elements can have ARIA roles
    if not isinstance(node, Element):
        return None

    element = node

    # Check explicit role
    if "role" in element.attrs:
        return element.attrs["role"]

    # Check implicit roles - use casefold() for better performance and Unicode handling
    tag = sys.intern(element.tag.casefold())

    if tag in _ROLE_MAP:
        return _ROLE_MAP[tag]

    # Special handling for input elements
    if tag == sys.intern("input"):
        input_type = sys.intern((element.attrs.get("type") or "text").casefold())
        return _INPUT_TYPE_MAP.get(input_type, sys.intern("textbox"))

    return None


def query_all_by_role(
    container: Container,
    role: AriaRole,
    *,
    level: int | None = None,
    name: str | re.Pattern[str] | None = None,
    _max_results: int | None = None,
) -> list[Element]:
    """Find all elements with the specified role.

    Args:
        container: The container to search within
        role: The ARIA role to search for
        level: Heading level for heading roles (keyword-only)
        name: Accessible name to match (keyword-only)
        _max_results: Internal parameter for early exit optimization

    Returns:
        List of elements matching the criteria
    """
    # Skip container element itself if container is an Element
    skip_container = isinstance(container, Element)

    # For role+name queries, we can't use max_results in get_all_elements
    # because we need to filter by name after getting role matches
    if name is not None:
        elements = get_all_elements(container, skip_root=skip_container)
    else:
        # Use early exit for role-only queries
        elements = get_all_elements(
            container, skip_root=skip_container, max_results=_max_results
        )

    results = []
    for element in elements:
        element_role = get_role_for_element(element)
        if element_role != role:
            continue

        # Check heading level
        if level is not None and role == "heading":
            if element.tag.casefold() == f"h{level}":
                pass  # Match
            elif "aria-level" in element.attrs:
                try:
                    aria_level_str = element.attrs["aria-level"]
                    if aria_level_str and int(aria_level_str) != level:
                        continue
                except ValueError:
                    continue
            else:
                continue

        # Check accessible name (lazy evaluation - only if needed)
        if name is not None:
            element_name = get_accessible_name(element, element_role)
            if isinstance(name, re.Pattern):
                # Regex pattern matching
                if not name.search(element_name):
                    continue
            else:
                # String substring matching
                if name not in element_name:
                    continue

        results.append(element)

        # Early exit if we've found enough results
        if _max_results is not None and len(results) >= _max_results:
            return results

    return results


def get_by_role(
    container: Container,
    role: AriaRole,
    *,
    level: int | None = None,
    name: str | re.Pattern[str] | None = None,
) -> Element:
    """Find a single element with the specified role.

    Args:
        container: The container to search within
        role: The ARIA role to search for
        level: Heading level for heading roles (keyword-only)
        name: Accessible name to match (keyword-only)

    Returns:
        Single element matching the criteria

    Raises:
        ElementNotFoundError: If no element found
        MultipleElementsError: If multiple elements found
    """
    elements = query_all_by_role(container, role, level=level, name=name)
    if not elements:
        raise ElementNotFoundError(f"Unable to find element with role '{role}'")
    if len(elements) > 1:
        raise MultipleElementsError(
            f"Found multiple elements with role '{role}'", count=len(elements)
        )
    return elements[0]


def query_by_role(
    container: Container,
    role: AriaRole,
    *,
    level: int | None = None,
    name: str | re.Pattern[str] | None = None,
) -> Element | None:
    """Find a single element with the specified role, return None if not found.

    Args:
        container: The container to search within
        role: The ARIA role to search for
        level: Heading level for heading roles (keyword-only)
        name: Accessible name to match (keyword-only)

    Returns:
        Single element if found, None otherwise
    """
    elements = query_all_by_role(container, role, level=level, name=name)
    return elements[0] if elements else None


def get_all_by_role(
    container: Container,
    role: AriaRole,
    *,
    level: int | None = None,
    name: str | re.Pattern[str] | None = None,
) -> list[Element]:
    """Find all elements with the specified role, raise error if none found.

    Args:
        container: The container to search within
        role: The ARIA role to search for
        level: Heading level for heading roles (keyword-only)
        name: Accessible name to match (keyword-only)

    Returns:
        List of elements matching the criteria

    Raises:
        ElementNotFoundError: If no elements found
    """
    elements = query_all_by_role(container, role, level=level, name=name)
    if not elements:
        raise ElementNotFoundError(f"Unable to find elements with role '{role}'")
    return elements


def query_all_by_text(
    container: Container, text: str, *, _max_results: int | None = None
) -> list[Element]:
    """Find all elements containing the specified text."""
    # Skip container element itself if container is an Element
    skip_container = isinstance(container, Element)
    elements = get_all_elements(container, skip_root=skip_container)

    results = []
    for element in elements:
        element_text = get_text_content(element)
        if text in element_text:
            results.append(element)
            # Early exit if we've found enough
            if _max_results is not None and len(results) >= _max_results:
                return results
    return results


# Generate query variants using factory
_, query_by_text, get_by_text, get_all_by_text = _make_query_variants(
    query_all_by_text, "text"
)


# Test ID-based queries
def query_all_by_test_id(
    container: Container, test_id: str, *, attribute: str = "data-testid"
) -> list[Element]:
    """
    Find all elements with the specified test ID.

    Args:
        container: The container node to search within
        test_id: The test ID value to match
        attribute: The attribute name to check (default: "data-testid")

    Returns:
        List of matching elements
    """
    return find_elements_by_attribute(container, attribute, test_id)


def query_by_test_id(
    container: Container, test_id: str, *, attribute: str = "data-testid"
) -> Element | None:
    """
    Find a single element with the specified test ID.

    Args:
        container: The container node to search within
        test_id: The test ID value to match
        attribute: The attribute name to check (default: "data-testid")

    Returns:
        The matching element, or None if not found
    """
    elements = query_all_by_test_id(container, test_id, attribute=attribute)
    return elements[0] if elements else None


def get_by_test_id(
    container: Container, test_id: str, *, attribute: str = "data-testid"
) -> Element:
    """
    Find a single element with the specified test ID.
    Throws an error if not found or multiple elements match.

    Args:
        container: The container node to search within
        test_id: The test ID value to match
        attribute: The attribute name to check (default: "data-testid")

    Returns:
        The matching element

    Raises:
        ElementNotFoundError: If no matching element is found
        MultipleElementsError: If multiple elements match
    """
    elements = query_all_by_test_id(container, test_id, attribute=attribute)

    if not elements:
        raise ElementNotFoundError(
            f"Unable to find element with {attribute}: {test_id}",
            suggestion="Check that the test ID is correct and the element exists",
        )

    if len(elements) > 1:
        raise MultipleElementsError(
            f"Found multiple elements with {attribute}: {test_id}", count=len(elements)
        )

    return elements[0]


def get_all_by_test_id(
    container: Container, test_id: str, *, attribute: str = "data-testid"
) -> list[Element]:
    """
    Find all elements with the specified test ID.
    Throws an error if no elements are found.

    Args:
        container: The container node to search within
        test_id: The test ID value to match
        attribute: The attribute name to check (default: "data-testid")

    Returns:
        List of matching elements

    Raises:
        ElementNotFoundError: If no matching elements are found
    """
    elements = query_all_by_test_id(container, test_id, attribute=attribute)

    if not elements:
        raise ElementNotFoundError(
            f"Unable to find elements with {attribute}: {test_id}",
            suggestion="Check that the test ID is correct and elements exist",
        )

    return elements


# ID-based queries


def query_by_id(container: Container, element_id: str) -> Element | None:
    """
    Find a single element with the specified HTML id attribute.

    Args:
        container: The container node to search within
        element_id: The value of the element's id attribute

    Returns:
        The matching element, or None if not found
    """
    elements = find_elements_by_attribute(container, "id", element_id)
    return elements[0] if elements else None


def get_by_id(container: Container, element_id: str) -> Element:
    """
    Find a single element with the specified HTML id attribute.
    Throws an error if not found or multiple elements match.

    Args:
        container: The container node to search within
        element_id: The value of the element's id attribute

    Returns:
        The matching element

    Raises:
        ElementNotFoundError: If no matching element is found
        MultipleElementsError: If multiple elements match (duplicate ids)
    """
    elements = find_elements_by_attribute(container, "id", element_id)

    if not elements:
        raise ElementNotFoundError(
            f"Unable to find element with id: {element_id}",
            suggestion="Check that the id is correct and the element exists",
        )

    if len(elements) > 1:
        raise MultipleElementsError(
            f"Found multiple elements with id: {element_id}", count=len(elements)
        )

    return elements[0]


# Class-based queries


def _elements_with_class(
    container: Container, class_name: str, *, _max_results: int | None = None
) -> list[Element]:
    """Return all elements whose class attribute contains class_name as a token.

    HTML class attributes are a space-separated list of tokens. This matches
    by token equality, not substring.

    Uses set for O(1) lookup when checking class membership.
    """
    # Skip container element itself if container is an Element
    skip_container = isinstance(container, Element)
    results = []
    for el in get_all_elements(container, skip_root=skip_container):
        cls = el.attrs.get("class")
        if isinstance(cls, str):
            # Convert to set for O(1) lookup instead of O(n) list membership
            class_tokens = set(cls.split())
            if class_name in class_tokens:
                results.append(el)
                # Early exit if we've found enough
                if _max_results is not None and len(results) >= _max_results:
                    return results
    return results


def query_all_by_class(
    container: Container, class_name: str, *, _max_results: int | None = None
) -> list[Element]:
    """Find all elements that have the given CSS class token.

    Returns a (possibly empty) list of matches.
    """
    return _elements_with_class(container, class_name, _max_results=_max_results)


# Generate query variants using factory
_, query_by_class, get_by_class, get_all_by_class = _make_query_variants(
    query_all_by_class, "class"
)


# Helper function for finding form controls (moved to module level for performance)
def _find_form_controls(element: Element) -> list[Element]:
    """Find all form control descendants of an element."""
    results = []

    def traverse(node):
        if isinstance(node, Element):
            if node.tag.casefold() in {"input", "textarea", "select", "button"}:
                results.append(node)
            if hasattr(node, "children"):
                for child in node.children:
                    traverse(child)

    traverse(element)
    return results


# Label text search strategies (extracted for clarity)
def _find_by_aria_label(elements: list[Element], text: str) -> list[Element]:
    """Find elements with aria-label containing the text."""
    return [
        element
        for element in elements
        if (aria_label := element.attrs.get("aria-label")) and text in aria_label
    ]


def _find_by_label_for(
    elements: list[Element], label_elements: list[Element], text: str
) -> list[Element]:
    """Find elements associated with <label> via 'for' attribute."""
    results = []
    for label in label_elements:
        label_text = get_text_content(label)
        if text in label_text:
            label_for = label.attrs.get("for")
            if label_for:
                for element in elements:
                    if element.attrs.get("id") == label_for:
                        results.append(element)
    return results


def _find_by_nested_labels(label_elements: list[Element], text: str) -> list[Element]:
    """Find form controls nested inside <label> elements containing the text."""
    results = []
    for label in label_elements:
        label_text = get_text_content(label)
        if text in label_text:
            nested_controls = _find_form_controls(label)
            results.extend(nested_controls)
    return results


def _find_by_aria_labelledby(elements: list[Element], text: str) -> list[Element]:
    """Find elements with aria-labelledby referencing elements containing the text."""
    results = []
    for element in elements:
        aria_labelledby = element.attrs.get("aria-labelledby")
        if aria_labelledby:
            label_ids = aria_labelledby.split()
            for label_id in label_ids:
                for potential_label in elements:
                    if potential_label.attrs.get("id") == label_id:
                        label_text = get_text_content(potential_label)
                        if text in label_text:
                            results.append(element)
                            break
    return results


# Label text-based queries
def _query_all_by_label_text_impl(
    container: Container,
    text: str,
    find_first: bool = False,
    max_results: int | None = None,
) -> list[Element]:
    """Internal implementation with optional early exit for single-element queries."""
    # Skip container element itself if container is an Element
    skip_container = isinstance(container, Element)
    elements = get_all_elements(container, skip_root=skip_container)

    results = []

    # Strategy 1: Find by aria-label
    aria_label_matches = _find_by_aria_label(elements, text)
    results.extend(aria_label_matches)
    if find_first and results:
        return results

    # Get all label elements for remaining strategies
    label_elements = [el for el in elements if el.tag.casefold() == "label"]

    # Strategy 2: Find by <label for="id">
    label_for_matches = _find_by_label_for(elements, label_elements, text)
    results.extend(label_for_matches)
    if find_first and results:
        return results

    # Strategy 3: Find by nested form controls in <label>
    nested_matches = _find_by_nested_labels(label_elements, text)
    results.extend(nested_matches)
    if find_first and results:
        return results

    # Strategy 4: Find by aria-labelledby
    labelledby_matches = _find_by_aria_labelledby(elements, text)
    results.extend(labelledby_matches)

    # Remove duplicates while preserving order using dict
    # Dict maintains insertion order since Python 3.7+
    # Use id() as key since Element instances need identity-based uniqueness
    unique_results = list({id(el): el for el in results}.values())

    # Apply max_results if specified
    if max_results is not None:
        return unique_results[:max_results]
    return unique_results


def query_all_by_label_text(
    container: Container, text: str, *, _max_results: int | None = None
) -> list[Element]:
    """Find all elements with the specified label text.

    This function looks for elements that have:
    1. An aria-label attribute matching the text
    2. A <label> element that contains the text and is associated with the element via:
       - The for attribute pointing to the element's id
       - Nesting the element inside the label
    3. An aria-labelledby attribute pointing to an element with the text
    """
    return _query_all_by_label_text_impl(
        container, text, find_first=False, max_results=_max_results
    )


# Special case: query_by uses early-exit optimization
def query_by_label_text(container: Container, text: str) -> Element | None:
    """Find a single element with the specified label text, return None if not found."""
    elements = _query_all_by_label_text_impl(container, text, find_first=True)
    return elements[0] if elements else None


# Generate get_by and get_all_by variants using factory
_, _, get_by_label_text, get_all_by_label_text = _make_query_variants(
    query_all_by_label_text, "label text"
)


# Tag name-based queries with optional attribute filtering


def query_all_by_tag_name(
    container: Container, tag: str, *, attrs: dict[str, str] | None = None
) -> list[Element]:
    """Find all elements with the specified tag name.

    Args:
        container: The container to search within
        tag: The HTML tag name to search for (case-insensitive)
        attrs: Optional dictionary of attribute name/value pairs to filter by.
               Special attribute name "in_class" checks if value is contained in class string.

    Returns:
        List of elements matching the criteria

    Example:
        # Find all links
        links = query_all_by_tag_name(container, "a")

        # Find all links with specific rel attribute
        stylesheets = query_all_by_tag_name(container, "link", attrs={"rel": "stylesheet"})

        # Find elements with a specific class (substring match)
        fixed_headers = query_all_by_tag_name(container, "header", attrs={"in_class": "is-fixed"})
    """
    from aria_testing.utils import find_elements_by_tag

    all_elements = find_elements_by_tag(container, tag)

    # If no attribute filtering requested, return all matching tags
    if attrs is None:
        return all_elements

    # Filter by attributes
    results = []
    for element in all_elements:
        # Check if all specified attributes match
        matches = True
        for attr_name, attr_value in attrs.items():
            if attr_name == "in_class":
                # Special handling: check if value is in the class attribute
                class_attr = element.attrs.get("class") or ""
                if attr_value not in class_attr:
                    matches = False
                    break
            else:
                # Regular attribute exact match
                if element.attrs.get(attr_name) != attr_value:
                    matches = False
                    break
        if matches:
            results.append(element)

    return results


def query_by_tag_name(
    container: Container, tag: str, *, attrs: dict[str, str] | None = None
) -> Element | None:
    """Find a single element with the specified tag name, return None if not found.

    Args:
        container: The container to search within
        tag: The HTML tag name to search for (case-insensitive)
        attrs: Optional dictionary of attribute name/value pairs to filter by

    Returns:
        Single element if found, None otherwise
    """
    elements = query_all_by_tag_name(container, tag, attrs=attrs)
    return elements[0] if elements else None


def get_by_tag_name(
    container: Container, tag: str, *, attrs: dict[str, str] | None = None
) -> Element:
    """Find a single element with the specified tag name.

    Args:
        container: The container to search within
        tag: The HTML tag name to search for (case-insensitive)
        attrs: Optional dictionary of attribute name/value pairs to filter by

    Returns:
        Single element matching the criteria

    Raises:
        ElementNotFoundError: If no element found
        MultipleElementsError: If multiple elements found
    """
    elements = query_all_by_tag_name(container, tag, attrs=attrs)
    if not elements:
        attr_str = f" with attrs {attrs}" if attrs else ""
        raise ElementNotFoundError(f"Unable to find element with tag '{tag}'{attr_str}")
    if len(elements) > 1:
        attr_str = f" with attrs {attrs}" if attrs else ""
        raise MultipleElementsError(
            f"Found multiple elements with tag '{tag}'{attr_str}",
            count=len(elements),
        )
    return elements[0]


def get_all_by_tag_name(
    container: Container, tag: str, *, attrs: dict[str, str] | None = None
) -> list[Element]:
    """Find all elements with the specified tag name, raise error if none found.

    Args:
        container: The container to search within
        tag: The HTML tag name to search for (case-insensitive)
        attrs: Optional dictionary of attribute name/value pairs to filter by

    Returns:
        List of elements matching the criteria

    Raises:
        ElementNotFoundError: If no elements found
    """
    elements = query_all_by_tag_name(container, tag, attrs=attrs)
    if not elements:
        attr_str = f" with attrs {attrs}" if attrs else ""
        raise ElementNotFoundError(
            f"Unable to find elements with tag '{tag}'{attr_str}"
        )
    return elements
