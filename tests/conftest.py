"""Pytest configuration and fixtures."""

import pytest

from aria_testing import clear_all_caches


@pytest.fixture(autouse=True)
def clear_caches_between_tests():
    """Clear all caches between test runs to avoid cache pollution."""
    clear_all_caches()
    yield
    clear_all_caches()
