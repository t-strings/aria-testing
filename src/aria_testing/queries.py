"""
Query functions for finding elements in tdom trees using accessibility patterns.

All query functions accept both Element and Fragment containers, allowing you to
search within any tdom structure returned by html().
"""

import re
from typing import Literal

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

# ARIA Role Type Definitions
# Based on WAI-ARIA 1.1 specification and HTML living standard

# Landmark Roles - Define page structure and navigation
LandmarkRole = Literal[
    "banner",  # <header> (when not descendant of article/section)
    "complementary",  # <aside>
    "contentinfo",  # <footer> (when not descendant of article/section)
    "form",  # <form> (when has accessible name)
    "main",  # <main>
    "navigation",  # <nav>
    "region",  # <section> (when has accessible name)
    "search",  # No implicit HTML element
]

# Document Structure Roles - Organize content
DocumentStructureRole = Literal[
    "article",  # <article>
    "document",  # <body>, <html>
    "feed",  # No implicit HTML element
    "figure",  # <figure>
    "img",  # <img>
    "list",  # <ul>, <ol>
    "listitem",  # <li>
    "math",  # <math>
    "none",  # No implicit HTML element
    "presentation",  # No implicit HTML element
    "table",  # <table>
    "rowgroup",  # <tbody>, <thead>, <tfoot>
    "row",  # <tr>
    "cell",  # <td>
    "columnheader",  # <th scope="col">
    "rowheader",  # <th scope="row">
    "gridcell",  # No implicit HTML element
    "heading",  # <h1>-<h6>
    "separator",  # <hr>
]

# Widget Roles - Interactive elements
WidgetRole = Literal[
    "button",  # <button>, <input type="button|submit|reset">
    "checkbox",  # <input type="checkbox">
    "gridcell",  # No implicit HTML element
    "link",  # <a href="...">
    "menuitem",  # No implicit HTML element
    "menuitemcheckbox",  # No implicit HTML element
    "menuitemradio",  # No implicit HTML element
    "option",  # <option>
    "progressbar",  # <progress>
    "radio",  # <input type="radio">
    "scrollbar",  # No implicit HTML element
    "searchbox",  # <input type="search">
    "slider",  # <input type="range">
    "spinbutton",  # <input type="number">
    "switch",  # No implicit HTML element
    "tab",  # No implicit HTML element
    "tabpanel",  # No implicit HTML element
    "textbox",  # <input type="text|email|password|tel|url">, <textarea>
    "treeitem",  # No implicit HTML element
]

# Composite Widget Roles - Complex interactive elements
CompositeWidgetRole = Literal[
    "combobox",  # <select>, <input list="...">
    "grid",  # No implicit HTML element
    "listbox",  # <select multiple>
    "menu",  # No implicit HTML element
    "menubar",  # No implicit HTML element
    "radiogroup",  # No implicit HTML element
    "tablist",  # No implicit HTML element
    "tree",  # No implicit HTML element
    "treegrid",  # No implicit HTML element
]

# Live Region Roles - Dynamic content
LiveRegionRole = Literal[
    "alert",  # No implicit HTML element
    "log",  # No implicit HTML element
    "marquee",  # No implicit HTML element
    "status",  # <output>
    "timer",  # No implicit HTML element
]

# Window Roles - Application-like interfaces
WindowRole = Literal[
    "alertdialog",  # No implicit HTML element
    "dialog",  # <dialog>
]

# Combined type for all ARIA roles
AriaRole = (
    LandmarkRole
    | DocumentStructureRole
    | WidgetRole
    | CompositeWidgetRole
    | LiveRegionRole
    | WindowRole
)

# Most commonly used roles (subset for convenience)
CommonRole = Literal[
    # Landmarks
    "main",
    "navigation",
    "banner",
    "contentinfo",
    "complementary",
    "form",
    # Document structure
    "heading",
    "list",
    "listitem",
    "table",
    "row",
    "cell",
    "img",
    # Interactive elements
    "button",
    "link",
    "textbox",
    "checkbox",
    "radio",
    "combobox",
]


# Note: Using keyword-only arguments with * separator instead of options dictionary


def get_role_for_element(node: Node) -> str | None:
    """Get the ARIA role for a node (only Elements can have roles)."""
    # Only Elements can have ARIA roles
    if not isinstance(node, Element):
        return None

    element = node

    # Check explicit role
    if "role" in element.attrs:
        return element.attrs["role"]

    # Check implicit roles
    tag = element.tag.lower()
    role_map = {
        "button": "button",
        "summary": "button",  # <summary> has implicit role of button
        "nav": "navigation",
        "main": "main",
        "header": "banner",
        "footer": "contentinfo",
        "aside": "complementary",
        "h1": "heading",
        "h2": "heading",
        "h3": "heading",
        "h4": "heading",
        "h5": "heading",
        "h6": "heading",
        "a": "link",
        "ul": "list",
        "ol": "list",
        "li": "listitem",
        "form": "form",
        "img": "img",
        "textarea": "textbox",
    }

    if tag in role_map:
        return role_map[tag]

    # Special handling for input elements
    if tag == "input":
        input_type = (element.attrs.get("type") or "text").lower()
        type_map = {
            "text": "textbox",
            "email": "textbox",
            "password": "textbox",
            "number": "spinbutton",
            "checkbox": "checkbox",
            "radio": "radio",
            "button": "button",
            "submit": "button",
            "reset": "button",
        }
        return type_map.get(input_type, "textbox")

    return None


def query_all_by_role(
    container: Container,
    role: AriaRole,
    *,
    level: int | None = None,
    name: str | re.Pattern[str] | None = None,
) -> list[Element]:
    """Find all elements with the specified role.

    Args:
        container: The container to search within
        role: The ARIA role to search for
        level: Heading level for heading roles (keyword-only)
        name: Accessible name to match (keyword-only)

    Returns:
        List of elements matching the criteria
    """
    all_elements = get_all_elements(container)
    # Skip container itself if it's an element
    if isinstance(container, Element) and all_elements and all_elements[0] is container:
        elements = all_elements[1:]
    else:
        elements = all_elements

    results = []
    for element in elements:
        element_role = get_role_for_element(element)
        if element_role != role:
            continue

        # Check heading level
        if level is not None and role == "heading":
            if element.tag.lower() == f"h{level}":
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

        # Check accessible name
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


def query_all_by_text(container: Container, text: str) -> list[Element]:
    """Find all elements containing the specified text."""
    all_elements = get_all_elements(container)
    # Skip container itself if it's an element
    if isinstance(container, Element) and all_elements and all_elements[0] is container:
        elements = all_elements[1:]
    else:
        elements = all_elements

    results = []
    for element in elements:
        element_text = get_text_content(element)
        if text in element_text:
            results.append(element)
    return results


def get_by_text(container: Container, text: str) -> Element:
    """Find a single element containing the specified text."""
    elements = query_all_by_text(container, text)
    if not elements:
        raise ElementNotFoundError(f"Unable to find element with text: {text}")
    if len(elements) > 1:
        raise MultipleElementsError(
            f"Found multiple elements with text: {text}", count=len(elements)
        )
    return elements[0]


def query_by_text(container: Container, text: str) -> Element | None:
    """Find a single element containing the specified text, return None if not found."""
    elements = query_all_by_text(container, text)
    return elements[0] if elements else None


def get_all_by_text(container: Container, text: str) -> list[Element]:
    """Find all elements containing the specified text, raise error if none found."""
    elements = query_all_by_text(container, text)
    if not elements:
        raise ElementNotFoundError(f"Unable to find elements with text: {text}")
    return elements


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


def _elements_with_class(container: Container, class_name: str) -> list[Element]:
    """Return all elements whose class attribute contains class_name as a token.

    HTML class attributes are a space-separated list of tokens. This matches
    by token equality, not substring.
    """
    return [
        el
        for el in get_all_elements(container)
        if isinstance(cls := el.attrs.get("class"), str)
        and class_name in [t for t in cls.split() if t]
    ]


def query_all_by_class(container: Container, class_name: str) -> list[Element]:
    """Find all elements that have the given CSS class token.

    Returns a (possibly empty) list of matches.
    """
    return _elements_with_class(container, class_name)


def get_all_by_class(container: Container, class_name: str) -> list[Element]:
    """Find all elements that have the given CSS class token.

    Raises ElementNotFoundError if none match.
    """
    elements = _elements_with_class(container, class_name)
    if not elements:
        raise ElementNotFoundError(
            f"Unable to find elements with class: {class_name}",
            suggestion="Ensure at least one element has the specified class",
        )
    return elements


def query_by_class(container: Container, class_name: str) -> Element | None:
    """Find a single element that has the given CSS class token.

    Returns the element if exactly one match exists, None if none, and raises
    MultipleElementsError if more than one element matches.
    """
    elements = _elements_with_class(container, class_name)
    if not elements:
        return None
    if len(elements) > 1:
        raise MultipleElementsError(
            f"Found multiple elements with class: {class_name}", count=len(elements)
        )
    return elements[0]


def get_by_class(container: Container, class_name: str) -> Element:
    """Find a single element that has the given CSS class token.

    Raises ElementNotFoundError if none match and MultipleElementsError if more
    than one element matches.
    """
    elements = _elements_with_class(container, class_name)
    if not elements:
        raise ElementNotFoundError(
            f"Unable to find element with class: {class_name}",
            suggestion="Ensure the class exists on a rendered element",
        )
    if len(elements) > 1:
        raise MultipleElementsError(
            f"Found multiple elements with class: {class_name}", count=len(elements)
        )
    return elements[0]


# Label text-based queries
def query_all_by_label_text(container: Container, text: str) -> list[Element]:
    """Find all elements with the specified label text.

    This function looks for elements that have:
    1. An aria-label attribute matching the text
    2. A <label> element that contains the text and is associated with the element via:
       - The for attribute pointing to the element's id
       - Nesting the element inside the label
    3. An aria-labelledby attribute pointing to an element with the text
    """
    all_elements = get_all_elements(container)
    # Skip container itself if it's an element
    if isinstance(container, Element) and all_elements and all_elements[0] is container:
        elements = all_elements[1:]
    else:
        elements = all_elements

    results = []

    # First, find elements with aria-label attributes
    for element in elements:
        aria_label = element.attrs.get("aria-label")
        if aria_label and text in aria_label:
            results.append(element)

    # Then find elements with associated labels
    # Get all label elements in the container
    label_elements = [el for el in elements if el.tag.lower() == "label"]

    for label in label_elements:
        label_text = get_text_content(label)
        if text in label_text:
            # Check if this label is associated with any elements
            # Method 1: Check for 'for' attribute
            label_for = label.attrs.get("for")
            if label_for:
                # Find the element with this id
                for element in elements:
                    if element.attrs.get("id") == label_for:
                        results.append(element)

            # Method 2: Check for nested form controls
            nested_controls = []

            def find_nested_controls(node):
                if isinstance(node, Element):
                    if node.tag.lower() in ["input", "textarea", "select", "button"]:
                        nested_controls.append(node)
                    if hasattr(node, "children"):
                        for child in node.children:
                            find_nested_controls(child)

            find_nested_controls(label)
            results.extend(nested_controls)

    # Finally, check for aria-labelledby
    for element in elements:
        aria_labelledby = element.attrs.get("aria-labelledby")
        if aria_labelledby:
            # Split space-separated IDs
            label_ids = aria_labelledby.split()
            for label_id in label_ids:
                # Find the element with this ID
                for potential_label in elements:
                    if potential_label.attrs.get("id") == label_id:
                        label_text = get_text_content(potential_label)
                        if text in label_text:
                            results.append(element)
                            break

    # Remove duplicates while preserving order using dict
    # Dict maintains insertion order since Python 3.7+
    # Use id() as key since Element instances need identity-based uniqueness
    return list({id(el): el for el in results}.values())


def get_by_label_text(container: Container, text: str) -> Element:
    """Find a single element with the specified label text."""
    elements = query_all_by_label_text(container, text)
    if not elements:
        raise ElementNotFoundError(f"Unable to find element with label text: {text}")
    if len(elements) > 1:
        raise MultipleElementsError(
            f"Found multiple elements with label text: {text}", count=len(elements)
        )
    return elements[0]


def query_by_label_text(container: Container, text: str) -> Element | None:
    """Find a single element with the specified label text, return None if not found."""
    elements = query_all_by_label_text(container, text)
    return elements[0] if elements else None


def get_all_by_label_text(container: Container, text: str) -> list[Element]:
    """Find all elements with the specified label text, raise error if none found."""
    elements = query_all_by_label_text(container, text)
    if not elements:
        raise ElementNotFoundError(f"Unable to find elements with label text: {text}")
    return elements


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
