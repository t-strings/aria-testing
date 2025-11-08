"""
Custom exceptions for the aria_testing library.
"""

from typing import Optional


class AriaTestingLibraryError(Exception):
    """Base exception for all testing library errors."""

    pass


class ElementNotFoundError(AriaTestingLibraryError):
    """Raised when a get_by_* query fails to find any matching elements."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.suggestion = suggestion
        full_message = message
        if suggestion:
            full_message += f"\n\nSuggestion: {suggestion}"
        super().__init__(full_message)


class MultipleElementsError(AriaTestingLibraryError):
    """Raised when a get_by_* query finds multiple matching elements."""

    def __init__(self, message: str, count: int):
        self.count = count
        super().__init__(
            f"{message}\n\n(Found {count} elements. If this is intentional, use query_all_by_* instead.)"
        )
