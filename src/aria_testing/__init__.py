"""
aria_testing: A Python DOM Testing Library for tdom

This library provides accessibility-focused query functions that work with tdom's
Node, Element, Text, and Fragment types. It follows DOM Testing Library's philosophy:
"The more your tests resemble the way your software is used, the more confidence they can give you."
"""

from .assertions import (
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
from .cache import (
    CacheContext,
    clear_all_caches,
    get_cache_stats,
    print_cache_stats,
)
from .errors import AriaTestingLibraryError, ElementNotFoundError, MultipleElementsError
from .queries import (
    AriaRole,
    Container,
    get_all_by_class,
    get_all_by_label_text,
    get_all_by_role,
    get_all_by_tag_name,
    get_all_by_test_id,
    get_all_by_text,
    get_by_class,
    get_by_id,
    get_by_label_text,
    get_by_role,
    get_by_tag_name,
    get_by_test_id,
    get_by_text,
    query_all_by_class,
    query_all_by_label_text,
    query_all_by_role,
    query_all_by_tag_name,
    query_all_by_test_id,
    query_all_by_text,
    query_by_class,
    query_by_id,
    query_by_label_text,
    query_by_role,
    query_by_tag_name,
    query_by_test_id,
    query_by_text,
)
from .utils import get_text_content, normalize_text

__all__ = [
    # Query functions
    "get_by_text",
    "query_by_text",
    "get_all_by_text",
    "query_all_by_text",
    "get_by_test_id",
    "query_by_test_id",
    "get_all_by_test_id",
    "query_all_by_test_id",
    "get_by_role",
    "query_by_role",
    "get_all_by_role",
    "query_all_by_role",
    "get_by_label_text",
    "query_by_label_text",
    "get_all_by_label_text",
    "query_all_by_label_text",
    "get_by_tag_name",
    "query_by_tag_name",
    "get_all_by_tag_name",
    "query_all_by_tag_name",
    "get_by_id",
    "query_by_id",
    "get_by_class",
    "query_by_class",
    "get_all_by_class",
    "query_all_by_class",
    # Assertion helpers
    "GetByRole",
    "GetByText",
    "GetByLabelText",
    "GetByTestId",
    "GetByClass",
    "GetById",
    "GetByTagName",
    "GetAllByRole",
    "GetAllByText",
    "GetAllByLabelText",
    "GetAllByTestId",
    "GetAllByClass",
    "GetAllByTagName",
    # Utilities
    "get_text_content",
    "normalize_text",
    # Errors
    "AriaTestingLibraryError",
    "ElementNotFoundError",
    "MultipleElementsError",
    # Cache management
    "CacheContext",
    "clear_all_caches",
    "get_cache_stats",
    "print_cache_stats",
    # Type exports
    "AriaRole",
    "Container",
]
