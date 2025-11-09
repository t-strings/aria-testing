"""
Utility functions for text extraction and normalization from tdom nodes.
"""

import re
from typing import Callable

from tdom import Node, Element, Text, Fragment


def get_text_content(node: Node) -> str:
    """
    Extract all text content from a tdom node, similar to textContent in DOM.

    Args:
        node: The tdom node to extract text from

    Returns:
        The concatenated text content of the node and all its descendants
    """
    match node:
        case Text():
            return node.text
        case Element() | Fragment():
            return "".join(get_text_content(child) for child in node.children)
        case _:
            # For other node types (Comment, DocumentType), return empty string
            return ""


def normalize_text(
    text: str, *, collapse_whitespace: bool = True, trim: bool = True
) -> str:
    """
    Normalize text for matching purposes.

    Args:
        text: The text to normalize
        collapse_whitespace: Whether to collapse multiple whitespace characters into single spaces
        trim: Whether to strip leading and trailing whitespace

    Returns:
        The normalized text
    """
    if collapse_whitespace:
        # Replace any sequence of whitespace characters with a single space
        text = re.sub(r"\s+", " ", text)

    if trim:
        text = text.strip()

    return text


def matches_text(
    element_text: str,
    matcher: str | re.Pattern[str],
    *,
    exact: bool = True,
    normalize: bool = True,
) -> bool:
    """
    Check if element text matches the given matcher.

    Args:
        element_text: The text content of the element
        matcher: String or regex pattern to match against
        exact: Whether to use exact matching (vs substring matching)
        normalize: Whether to normalize text before matching

    Returns:
        True if the text matches, False otherwise
    """
    if normalize:
        element_text = normalize_text(element_text)

    if isinstance(matcher, re.Pattern):
        return bool(matcher.search(element_text))
    elif isinstance(matcher, str):
        if normalize:
            matcher = normalize_text(matcher)

        if exact:
            return element_text == matcher
        else:
            return matcher.lower() in element_text.lower()
    else:
        return False


def _traverse_elements(
    container: Node,
    predicate: Callable[[Element], bool] | None = None,
    *,
    skip_root: bool = False,
) -> list[Element]:
    """
    Generic tree traversal that collects elements matching a predicate.

    Args:
        container: The container node to search within
        predicate: Optional function to test each element. If None, collects all elements.
        skip_root: If True and container is an Element, exclude the container itself

    Returns:
        List of matching elements
    """
    results: list[Element] = []

    def traverse(node: Node, is_root: bool = True) -> None:
        match node:
            case Element():
                # Add element if not skipping root or not at root
                if not (skip_root and is_root):
                    if predicate is None or predicate(node):
                        results.append(node)
                # Always traverse children
                for child in node.children:
                    traverse(child, False)
            case Fragment():
                # Fragments are never considered root for skipping
                for child in node.children:
                    traverse(child, False)

    traverse(container)
    return results


def find_elements_by_attribute(
    container: Node, attribute: str, value: str | None = None
) -> list[Element]:
    """
    Find all elements within container that have the specified attribute.

    Args:
        container: The container node to search within
        attribute: The attribute name to look for
        value: Optional specific value the attribute must have

    Returns:
        List of matching elements
    """

    def predicate(element: Element) -> bool:
        if attribute not in element.attrs:
            return False
        return value is None or element.attrs[attribute] == value

    return _traverse_elements(container, predicate)


def find_elements_by_tag(container: Node, tag: str) -> list[Element]:
    """
    Find all elements within container that have the specified tag name.

    Args:
        container: The container node to search within
        tag: The tag name to look for

    Returns:
        List of matching elements
    """
    tag_lower = tag.lower()
    return _traverse_elements(container, lambda el: el.tag.lower() == tag_lower)


def get_all_elements(container: Node, *, skip_root: bool = False) -> list[Element]:
    """
    Get all Element nodes within the container.

    Args:
        container: The container node to search within
        skip_root: If True and container is an Element, exclude the container itself

    Returns:
        List of all elements in the container
    """
    return _traverse_elements(container, skip_root=skip_root)


def get_accessible_name(element: Element, role: str | None = None) -> str:
    """
    Get the accessible name for an element based on its role and attributes.

    This follows the accessible name computation algorithm, checking:
    1. aria-label
    2. aria-labelledby (referenced element text)
    3. Role-specific naming (text content, href, alt, title)
    4. Text content fallback

    Args:
        element: The element to get the accessible name for
        role: The element's ARIA role (for role-specific behavior)

    Returns:
        The computed accessible name as a string
    """
    # Check aria-label first
    if "aria-label" in element.attrs:
        aria_label = element.attrs["aria-label"]
        if aria_label and aria_label.strip():
            return aria_label.strip()

    # Check aria-labelledby
    # Note: Full implementation would traverse the DOM to find elements by ID
    # and concatenate their text content. Skipped for now as it requires
    # container context which this function doesn't have.

    # Role-specific naming
    if role == "link":
        # For links: combine text content and href for name matching
        text = get_text_content(element).strip()
        href = element.attrs.get("href", "")

        # Combine text and href for comprehensive name matching
        name_parts = []
        if text:
            name_parts.append(text)
        if href:
            name_parts.append(href)

        if name_parts:
            return " ".join(name_parts)

        # If neither text nor href, fall through to general fallback

    elif role == "button":
        # For buttons: text content is primary
        text = get_text_content(element).strip()
        if text:
            return text

    elif role == "img":
        # For images: alt text is primary
        if "alt" in element.attrs:
            alt = element.attrs["alt"]
            if alt is not None:  # alt="" is valid
                return alt
        # Fallback to title
        if "title" in element.attrs:
            title = element.attrs["title"]
            if title and title.strip():
                return title.strip()

    elif role in ("textbox", "combobox", "listbox"):
        # For form controls, check value first, then placeholder, then text content
        if "value" in element.attrs:
            value = element.attrs["value"]
            if value and value.strip():
                return value.strip()
        if "placeholder" in element.attrs:
            placeholder = element.attrs["placeholder"]
            if placeholder and placeholder.strip():
                return placeholder.strip()

    # General fallback: text content
    text = get_text_content(element).strip()
    if text:
        return text

    # Final fallback: title attribute
    if "title" in element.attrs:
        title = element.attrs["title"]
        if title and title.strip():
            return title.strip()

    # No accessible name found
    return ""
