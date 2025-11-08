"""
Utility functions for text extraction and normalization from tdom nodes.
"""

import re
from typing import Union, Optional, Pattern

from tdom import Node, Element, Text, Fragment


def get_text_content(node: Node) -> str:
    """
    Extract all text content from a tdom node, similar to textContent in DOM.

    Args:
        node: The tdom node to extract text from

    Returns:
        The concatenated text content of the node and all its descendants
    """
    if isinstance(node, Text):
        return node.text
    elif isinstance(node, Element):
        return "".join(get_text_content(child) for child in node.children)
    elif isinstance(node, Fragment):
        return "".join(get_text_content(child) for child in node.children)
    else:
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
    matcher: Union[str, Pattern[str]],
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

    if hasattr(matcher, "search") and callable(
        getattr(matcher, "search")
    ):  # It's a regex pattern
        return bool(getattr(matcher, "search")(element_text))
    elif isinstance(matcher, str):
        if normalize:
            matcher = normalize_text(matcher)

        if exact:
            return element_text == matcher
        else:
            return matcher.lower() in element_text.lower()
    else:
        return False


def find_elements_by_attribute(
    container: Node, attribute: str, value: Optional[str] = None
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
    results: list[Element] = []

    def traverse(node: Node) -> None:
        if isinstance(node, Element):
            if attribute in node.attrs:
                if value is None or node.attrs[attribute] == value:
                    results.append(node)
            # Continue traversing children
            for child in node.children:
                traverse(child)
        elif isinstance(node, Fragment):
            for child in node.children:
                traverse(child)

    traverse(container)
    return results


def find_elements_by_tag(container: Node, tag: str) -> list[Element]:
    """
    Find all elements within container that have the specified tag name.

    Args:
        container: The container node to search within
        tag: The tag name to look for

    Returns:
        List of matching elements
    """
    results: list[Element] = []

    def traverse(node: Node) -> None:
        if isinstance(node, Element):
            if node.tag.lower() == tag.lower():
                results.append(node)
            # Continue traversing children
            for child in node.children:
                traverse(child)
        elif isinstance(node, Fragment):
            for child in node.children:
                traverse(child)

    traverse(container)
    return results


def get_all_elements(container: Node) -> list[Element]:
    """
    Get all Element nodes within the container.

    Args:
        container: The container node to search within

    Returns:
        List of all elements in the container
    """
    results: list[Element] = []

    def traverse(node: Node) -> None:
        if isinstance(node, Element):
            results.append(node)
            # Continue traversing children
            for child in node.children:
                traverse(child)
        elif isinstance(node, Fragment):
            for child in node.children:
                traverse(child)

    traverse(container)
    return results


def get_accessible_name(element: Element, role: Optional[str] = None) -> str:
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
    if "aria-labelledby" in element.attrs:
        labelledby_attr = element.attrs["aria-labelledby"]
        if labelledby_attr is not None:
            labelledby_attr.split()
            # In a real implementation, we would traverse the DOM to find elements with these IDs
            # For now, we'll skip this complex case and fall through to other methods
            pass

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
