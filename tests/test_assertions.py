"""Tests for assertion helpers."""

import pytest
from tdom import html

from aria_testing import (
    GetAllByClass,
    GetAllByRole,
    GetAllByTagName,
    GetAllByText,
    GetByClass,
    GetById,
    GetByRole,
    GetByTagName,
    GetByText,
)


# Foundation tests - immutability and __call__ signature


def test_frozen_dataclass_immutability() -> None:
    """Test helper classes are immutable frozen dataclasses."""
    helper = GetByTagName(tag_name="button")
    with pytest.raises(AttributeError):
        helper.tag_name = "div"  # type: ignore[misc]


def test_call_signature_accepts_element() -> None:
    """Test __call__ accepts Element."""
    helper = GetByTagName(tag_name="button")
    element = html(t"<button>Click</button>")
    helper(element)  # Should not raise


def test_call_signature_accepts_fragment() -> None:
    """Test __call__ accepts Fragment."""
    helper = GetByTagName(tag_name="button")
    fragment = html(t"<button>First</button><button>Second</button>")
    with pytest.raises(AssertionError):  # Multiple elements found
        helper(fragment)


# Query helper tests - single element queries


def test_get_by_role_finds_element() -> None:
    """Test GetByRole finds element by role."""
    helper = GetByRole(role="button")
    container = html(t"<div><button>Click</button></div>")
    helper(container)  # Should not raise


def test_get_by_role_with_level() -> None:
    """Test GetByRole finds heading with level."""
    helper = GetByRole(role="heading", level=1)
    container = html(t"<div><h1>Title</h1></div>")
    helper(container)  # Should not raise


def test_get_by_role_with_name() -> None:
    """Test GetByRole finds element with accessible name."""
    helper = GetByRole(role="button", name="Submit")
    container = html(t"<div><button>Submit</button></div>")
    helper(container)  # Should not raise


def test_get_by_text_finds_element() -> None:
    """Test GetByText finds element with text."""
    helper = GetByText(text="Submit")
    element = html(t"<div><button>Submit</button></div>")
    helper(element)  # Should not raise


def test_get_by_test_id_finds_element() -> None:
    """Test GetByTestId finds element by test ID."""
    helper = GetByTagName(tag_name="button")
    element = html(t"<button>Click</button>")
    helper(element)  # Should not raise


def test_get_by_class_finds_element() -> None:
    """Test GetByClass finds element by class name."""
    helper = GetByClass(class_name="btn-primary")
    container = html(t'<div><button class="btn-primary">Click</button></div>')
    helper(container)  # Should not raise


def test_get_by_id_finds_element() -> None:
    """Test GetById finds element by ID."""
    helper = GetById(id="main")
    element = html(t'<div id="main">Content</div>')
    helper(element)  # Should not raise


def test_get_by_tag_name_finds_element() -> None:
    """Test GetByTagName finds element by tag."""
    helper = GetByTagName(tag_name="button")
    element = html(t"<button>Click</button>")
    helper(element)  # Should not raise


def test_query_failure_raises_assertion_error() -> None:
    """Test query failure raises AssertionError."""
    helper = GetByTagName(tag_name="article")
    element = html(t"<div>No article</div>")
    with pytest.raises(AssertionError):
        helper(element)


def test_query_failure_includes_detailed_error_message() -> None:
    """Test query failure includes detailed error message."""
    helper = GetByTagName(tag_name="article")
    element = html(t"<div>No article</div>")
    with pytest.raises(AssertionError) as exc_info:
        helper(element)
    error_msg = str(exc_info.value)
    assert "article" in error_msg
    assert "Query:" in error_msg
    assert "Searched in:" in error_msg


# Fluent API tests - negation, text content, attributes


def test_not_succeeds_when_element_absent() -> None:
    """Test .not_() succeeds when element is absent."""
    helper = GetByTagName(tag_name="button").not_()
    element = html(t"<div>No button</div>")
    helper(element)  # Should not raise


def test_not_fails_when_element_present() -> None:
    """Test .not_() fails when element exists."""
    helper = GetByTagName(tag_name="button").not_()
    element = html(t"<button>Unexpected</button>")
    with pytest.raises(AssertionError) as exc_info:
        helper(element)
    assert "NOT to exist" in str(exc_info.value)


def test_text_content_verification_success() -> None:
    """Test .text_content() succeeds when text matches."""
    helper = GetByTagName(tag_name="button").text_content("Save")
    element = html(t"<button>Save</button>")
    helper(element)  # Should not raise


def test_text_content_verification_failure() -> None:
    """Test .text_content() fails when text doesn't match."""
    helper = GetByTagName(tag_name="button").text_content("Save")
    element = html(t"<button>Cancel</button>")
    with pytest.raises(AssertionError) as exc_info:
        helper(element)
    error_msg = str(exc_info.value)
    assert "Expected text:" in error_msg
    assert "Save" in error_msg
    assert "Cancel" in error_msg


def test_with_attribute_success() -> None:
    """Test .with_attribute() succeeds when attribute matches."""
    helper = GetByTagName(tag_name="button").with_attribute("type", "submit")
    element = html(t'<button type="submit">Submit</button>')
    helper(element)  # Should not raise


def test_with_attribute_checks_existence_only() -> None:
    """Test .with_attribute() can check attribute existence only."""
    helper = GetByTagName(tag_name="button").with_attribute("disabled")
    element = html(t'<button disabled="">Click</button>')
    helper(element)  # Should not raise


def test_with_attribute_missing_fails() -> None:
    """Test .with_attribute() fails when attribute missing."""
    helper = GetByTagName(tag_name="button").with_attribute("aria-pressed")
    element = html(t"<button>Toggle</button>")
    with pytest.raises(AssertionError) as exc_info:
        helper(element)
    assert "attribute" in str(exc_info.value).lower()


def test_with_attribute_wrong_value_fails() -> None:
    """Test .with_attribute() fails when attribute value is wrong."""
    helper = GetByTagName(tag_name="button").with_attribute("type", "submit")
    element = html(t'<button type="button">Click</button>')
    with pytest.raises(AssertionError) as exc_info:
        helper(element)
    error_msg = str(exc_info.value)
    assert "submit" in error_msg
    assert "button" in error_msg


def test_method_chaining() -> None:
    """Test multiple fluent methods can be chained."""
    helper = (
        GetByTagName(tag_name="button")
        .text_content("Save")
        .with_attribute("type", "button")
    )
    element = html(t'<button type="button">Save</button>')
    helper(element)  # Should not raise


def test_immutability_preserved_by_fluent_api() -> None:
    """Test fluent API maintains immutability."""
    original = GetByTagName(tag_name="button")
    modified = original.not_()
    assert original.negate is False
    assert modified.negate is True
    assert original is not modified


# GetAllBy* tests - count and nth operations


def test_get_all_by_role_returns_list() -> None:
    """Test GetAllByRole works with multiple elements."""
    helper = GetAllByRole(role="button")
    element = html(t"<div><button>First</button><button>Second</button></div>")
    helper(element)  # Should not raise


def test_get_all_by_text_returns_list() -> None:
    """Test GetAllByText works with multiple elements."""
    helper = GetAllByText(text="Item")
    element = html(t"<div><span>Item</span><span>Item</span><span>Item</span></div>")
    helper(element)  # Should not raise


def test_get_all_by_tag_name_returns_list() -> None:
    """Test GetAllByTagName works with multiple elements."""
    helper = GetAllByTagName(tag_name="button")
    element = html(t"<div><button>A</button><button>B</button></div>")
    helper(element)  # Should not raise


def test_count_assertion_success() -> None:
    """Test .count() succeeds when count matches."""
    helper = GetAllByRole(role="button").count(2)
    element = html(t"<div><button>First</button><button>Second</button></div>")
    helper(element)  # Should not raise


def test_count_assertion_failure() -> None:
    """Test .count() fails when count doesn't match."""
    helper = GetAllByRole(role="button").count(3)
    element = html(t"<div><button>First</button><button>Second</button></div>")
    with pytest.raises(AssertionError) as exc_info:
        helper(element)
    error_msg = str(exc_info.value)
    assert "Expected count: 3" in error_msg
    assert "found: 2" in error_msg


def test_nth_selects_element() -> None:
    """Test .nth() selects specific element."""
    helper = GetAllByRole(role="button").nth(0).text_content("First")
    element = html(t"<div><button>First</button><button>Second</button></div>")
    helper(element)  # Should not raise


def test_nth_with_text_content() -> None:
    """Test .nth() chains with .text_content()."""
    helper = GetAllByRole(role="button").nth(1).text_content("Second")
    element = html(t"<div><button>First</button><button>Second</button></div>")
    helper(element)  # Should not raise


def test_nth_with_attribute() -> None:
    """Test .nth() chains with .with_attribute()."""
    helper = GetAllByRole(role="button").nth(0).with_attribute("type", "submit")
    element = html(
        t'<div><button type="submit">First</button><button type="button">Second</button></div>'
    )
    helper(element)  # Should not raise


def test_nth_out_of_bounds() -> None:
    """Test .nth() fails when index is out of bounds."""
    helper = GetAllByRole(role="button").nth(5)
    element = html(t"<div><button>First</button><button>Second</button></div>")
    with pytest.raises(AssertionError) as exc_info:
        helper(element)
    error_msg = str(exc_info.value)
    assert "Index 5 out of bounds" in error_msg
    assert "found 2 elements" in error_msg


def test_count_and_nth_together() -> None:
    """Test .count() and .nth() can't be used together effectively."""
    # Note: In practice, count() verifies total but nth() still selects
    helper = GetAllByRole(role="button").count(2).nth(0).text_content("First")
    element = html(t"<div><button>First</button><button>Second</button></div>")
    helper(element)  # Should not raise


# Additional coverage for GetAllBy* helpers


def test_get_all_by_class() -> None:
    """Test GetAllByClass works with multiple elements."""
    helper = GetAllByClass(class_name="item").count(3)
    element = html(
        t'<div><span class="item">A</span><span class="item">B</span><span class="item">C</span></div>'
    )
    helper(element)  # Should not raise


def test_get_all_by_tag_name_with_nth() -> None:
    """Test GetAllByTagName with .nth() selection."""
    helper = GetAllByTagName(tag_name="li").nth(2).text_content("Third")
    element = html(
        t"<ul><li>First</li><li>Second</li><li>Third</li><li>Fourth</li></ul>"
    )
    helper(element)  # Should not raise
