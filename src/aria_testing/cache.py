"""
Caching infrastructure for performance optimization.

This module provides two main caching mechanisms:
1. Element list caching - Cache traversal results per container
2. Role computation caching - Cache computed roles per element

Both use weak references to avoid memory leaks when DOM nodes are garbage collected.
"""

import sys
from collections.abc import Callable
from typing import Any

from tdom import Element, Node


class CacheStats:
    """Statistics tracker for cache performance monitoring."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def record_hit(self):
        """Record a cache hit."""
        self.hits += 1

    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1

    def record_eviction(self):
        """Record a cache eviction (garbage collection)."""
        self.evictions += 1

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate (0.0 to 1.0)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def reset(self):
        """Reset all statistics to zero."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def __repr__(self) -> str:
        """Human-readable statistics."""
        total = self.hits + self.misses
        hit_rate = self.hit_rate * 100
        return (
            f"CacheStats(hits={self.hits}, misses={self.misses}, "
            f"hit_rate={hit_rate:.1f}%, evictions={self.evictions}, total={total})"
        )


class ElementListCache:
    """
    Cache for element traversal results.

    Uses id()-based dictionary since tdom nodes don't support weak references.
    Cache key is (id(container), skip_root) tuple.

    Note: Without weak references, cache must be manually cleared when needed.
    Thread-safe: No (assumes single-threaded usage in tests).
    """

    def __init__(self):
        # Regular dict mapping id(container) -> dict[skip_root -> list[Element]]
        # We can't use WeakKeyDictionary because tdom nodes don't support weakref
        self._cache: dict[int, dict[bool, list[Element]]] = {}
        self.stats = CacheStats()

    def get(self, container: Node, skip_root: bool) -> list[Element] | None:
        """
        Get cached element list for a container.

        Args:
            container: The container node
            skip_root: Whether root was skipped in traversal

        Returns:
            Cached element list or None if not found
        """
        container_id = id(container)

        if container_id not in self._cache:
            self.stats.record_miss()
            return None

        container_cache = self._cache[container_id]
        if skip_root not in container_cache:
            self.stats.record_miss()
            return None

        self.stats.record_hit()
        return container_cache[skip_root]

    def set(self, container: Node, skip_root: bool, elements: list[Element]):
        """
        Cache element list for a container.

        Args:
            container: The container node
            skip_root: Whether root was skipped in traversal
            elements: The element list to cache
        """
        container_id = id(container)

        if container_id not in self._cache:
            self._cache[container_id] = {}

        self._cache[container_id][skip_root] = elements

    def clear(self):
        """Clear all cached data and reset statistics."""
        self._cache.clear()
        self.stats.reset()

    def size(self) -> int:
        """Return number of containers currently cached."""
        return len(self._cache)

    def __repr__(self) -> str:
        """Human-readable cache status."""
        return f"ElementListCache(size={self.size()}, {self.stats})"


class RoleCache:
    """
    Cache for computed ARIA roles.

    Uses id()-based dictionary since tdom elements don't support weak references.
    Stores both successful role lookups and None results (negative caching).

    Note: Without weak references, cache must be manually cleared when needed.
    Thread-safe: No (assumes single-threaded usage in tests).
    """

    def __init__(self):
        # Regular dict mapping id(element) -> role string or None
        # We can't use WeakKeyDictionary because tdom elements don't support weakref
        self._cache: dict[int, str | None] = {}
        self.stats = CacheStats()

        # Intern sentinel for "not cached" to distinguish from cached None
        self._NOT_CACHED = sys.intern("__NOT_CACHED__")

    def get(self, element: Element) -> str | None | Any:
        """
        Get cached role for an element.

        Args:
            element: The element to look up

        Returns:
            Cached role string, None (if cached as None), or _NOT_CACHED sentinel
        """
        element_id = id(element)
        result = self._cache.get(element_id, self._NOT_CACHED)

        if result is self._NOT_CACHED:
            self.stats.record_miss()
            return self._NOT_CACHED

        self.stats.record_hit()
        return result

    def set(self, element: Element, role: str | None):
        """
        Cache computed role for an element.

        Args:
            element: The element
            role: The computed role (or None if no role)
        """
        element_id = id(element)
        self._cache[element_id] = role

    def clear(self):
        """Clear all cached data and reset statistics."""
        self._cache.clear()
        self.stats.reset()

    def size(self) -> int:
        """Return number of elements currently cached."""
        return len(self._cache)

    def __repr__(self) -> str:
        """Human-readable cache status."""
        return f"RoleCache(size={self.size()}, {self.stats})"


# Global cache instances (singleton pattern)
_element_list_cache = ElementListCache()
_role_cache = RoleCache()


def get_element_list_cache() -> ElementListCache:
    """Get the global element list cache instance."""
    return _element_list_cache


def get_role_cache() -> RoleCache:
    """Get the global role cache instance."""
    return _role_cache


def clear_all_caches():
    """Clear all global caches and reset statistics."""
    _element_list_cache.clear()
    _role_cache.clear()


def get_cache_stats() -> dict[str, CacheStats]:
    """
    Get statistics for all caches.

    Returns:
        Dictionary mapping cache name to its stats
    """
    return {
        "element_list": _element_list_cache.stats,
        "role": _role_cache.stats,
    }


def print_cache_stats():
    """Print human-readable cache statistics."""
    print("=" * 80)
    print("CACHE STATISTICS")
    print("=" * 80)
    print(f"Element List Cache: {_element_list_cache}")
    print(f"Role Cache:         {_role_cache}")
    print("=" * 80)


# Context manager for cache control
class CacheContext:
    """
    Context manager for controlling cache behavior.

    Usage:
        with CacheContext(enabled=False):
            # Caching disabled in this block
            elements = get_all_elements(container)
    """

    def __init__(self, enabled: bool = True, clear_on_exit: bool = False):
        """
        Initialize cache context.

        Args:
            enabled: Whether caching should be enabled
            clear_on_exit: Whether to clear caches when exiting context
        """
        self.enabled = enabled
        self.clear_on_exit = clear_on_exit
        self._prev_enabled: bool | None = None

    def __enter__(self):
        """Enter context - save previous state."""
        # Store previous state (for nested contexts)
        self._prev_enabled = getattr(_element_list_cache, "_enabled", True)
        _element_list_cache._enabled = self.enabled  # type: ignore
        _role_cache._enabled = self.enabled  # type: ignore
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - restore previous state."""
        # Restore previous state
        if self._prev_enabled is not None:
            _element_list_cache._enabled = self._prev_enabled  # type: ignore
            _role_cache._enabled = self._prev_enabled  # type: ignore

        # Clear if requested
        if self.clear_on_exit:
            clear_all_caches()


def with_caching(
    cache_getter: Callable[[], Any], cache_key_fn: Callable[..., Any]
) -> Callable:
    """
    Decorator to add caching to a function.

    This is a general-purpose caching decorator that can be used
    for any function that should cache its results.

    Args:
        cache_getter: Function that returns the cache instance
        cache_key_fn: Function that generates cache key from function arguments

    Returns:
        Decorated function with caching
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            cache = cache_getter()

            # Check if caching is enabled (via CacheContext)
            if not getattr(cache, "_enabled", True):
                return func(*args, **kwargs)

            # Generate cache key
            key = cache_key_fn(*args, **kwargs)

            # Try to get from cache
            result = cache.get(key)
            if result is not None or (
                hasattr(cache, "_NOT_CACHED") and result is not cache._NOT_CACHED
            ):
                return result

            # Cache miss - compute and store
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result

        wrapper.__wrapped__ = func  # type: ignore
        return wrapper

    return decorator
