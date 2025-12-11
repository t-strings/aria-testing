"""Assertion helpers for aria-testing.

This package provides frozen dataclass-based assertion helpers that wrap
aria-testing queries for declarative, type-safe assertions in tests.

Example:
    from aria_testing.assertions import GetByRole, GetByText, GetAllByRole

    container = html(t'<button>Submit</button>')

    # Single element assertions
    GetByRole(role="button")(container)
    GetByText(text="Submit")(container)
    GetByRole(role="button").text_content("Submit")(container)

    # List assertions
    GetAllByRole(role="button").count(3)(container)
    GetAllByRole(role="button").nth(0).text_content("First")(container)

    # Negative assertions
    GetByRole(role="link").not_()(container)
"""

from aria_testing.assertions.helpers import (
    GetAllByClass,
    GetAllByLabelText,
    GetAllByRole,
    GetAllByTagName,
    GetAllByTestId,
    GetAllByText,
    GetByClass,
    GetById,
    GetByLabelText,
    GetByRole,
    GetByTagName,
    GetByTestId,
    GetByText,
)

__all__ = [
    # Single element helpers
    "GetByRole",
    "GetByText",
    "GetByLabelText",
    "GetByTestId",
    "GetByClass",
    "GetById",
    "GetByTagName",
    # List-oriented helpers
    "GetAllByRole",
    "GetAllByText",
    "GetAllByLabelText",
    "GetAllByTestId",
    "GetAllByClass",
    "GetAllByTagName",
]
