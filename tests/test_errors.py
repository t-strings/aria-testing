"""
Tests for aria_testing.errors module.
"""

from aria_testing.errors import (
    AriaTestingLibraryError,
    ElementNotFoundError,
    MultipleElementsError,
)


def test_base_exception():
    error = AriaTestingLibraryError("Base error")
    assert str(error) == "Base error"
    assert isinstance(error, Exception)


def test_basic_error():
    error = ElementNotFoundError("Element not found")
    assert str(error) == "Element not found"
    assert isinstance(error, AriaTestingLibraryError)


def test_error_with_suggestion():
    error = ElementNotFoundError(
        "Element not found", suggestion="Try using a different selector"
    )
    expected = "Element not found\n\nSuggestion: Try using a different selector"
    assert str(error) == expected
    assert error.suggestion == "Try using a different selector"


def test_error_without_suggestion():
    error = ElementNotFoundError("Element not found")
    assert error.suggestion is None


def test_multiple_elements_error():
    error = MultipleElementsError("Found multiple elements", count=3)
    expected = "Found multiple elements\n\n(Found 3 elements. If this is intentional, use query_all_by_* instead.)"
    assert str(error) == expected
    assert error.count == 3
    assert isinstance(error, AriaTestingLibraryError)


def test_count_property():
    error = MultipleElementsError("Test", count=5)
    assert error.count == 5
