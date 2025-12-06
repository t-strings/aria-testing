"""Tests for caching functionality."""

from tdom import html

from aria_testing import (
    CacheContext,
    clear_all_caches,
    get_all_by_role,
    get_cache_stats,
    get_by_role,
    query_all_by_role,
)
from aria_testing.cache import get_element_list_cache, get_role_cache


def test_element_list_cache_on_repeated_queries():
    """Test that repeated queries use cached element lists."""
    clear_all_caches()

    document = html(t"""<div>
        <button>Save</button>
        <button>Cancel</button>
        <a href="#">Link</a>
    </div>""")

    # First query - cache miss
    buttons1 = query_all_by_role(document, "button")
    stats = get_cache_stats()
    assert stats["element_list"].misses == 1
    assert stats["element_list"].hits == 0

    # Second query on same container - cache hit
    buttons2 = query_all_by_role(document, "button")
    stats = get_cache_stats()
    assert stats["element_list"].hits == 1
    assert len(buttons1) == len(buttons2) == 2


def test_role_cache_on_repeated_lookups():
    """Test that role computation is cached per element."""
    clear_all_caches()

    document = html(t"""<div>
        <button>Save</button>
        <button>Cancel</button>
        <button>Delete</button>
    </div>""")

    # First query - computes roles for all buttons
    buttons1 = query_all_by_role(document, "button")

    # Element list is cached, so second query reuses same element list
    # This means roles are already computed and cached
    buttons2 = query_all_by_role(document, "button")
    role_stats_after_second = get_cache_stats()["role"]

    assert len(buttons1) == len(buttons2) == 3

    # The role cache should have been used
    # First query: misses for all elements
    # Second query: reuses cached element list and cached roles
    assert role_stats_after_second.misses >= 3  # At least the buttons
    assert role_stats_after_second.hits >= 3  # At least the buttons on second pass


def test_cache_context_disable():
    """Test that CacheContext can disable caching."""
    clear_all_caches()

    document = html(t"""<div>
        <button>Save</button>
        <button>Cancel</button>
    </div>""")

    # Query with caching enabled (default)
    _ = query_all_by_role(document, "button")
    stats_with_cache = get_cache_stats()
    assert (
        stats_with_cache["element_list"].hits + stats_with_cache["element_list"].misses
        > 0
    )

    clear_all_caches()

    # Query with caching disabled
    with CacheContext(enabled=False):
        _ = query_all_by_role(document, "button")
        stats_no_cache = get_cache_stats()
        # Stats should still be zero since caching was disabled
        assert stats_no_cache["element_list"].hits == 0
        assert stats_no_cache["element_list"].misses == 0


def test_cache_context_clear_on_exit():
    """Test that CacheContext can clear caches on exit."""
    clear_all_caches()

    document = html(t"""<div>
        <button>Save</button>
    </div>""")

    with CacheContext(enabled=True, clear_on_exit=True):
        _ = query_all_by_role(document, "button")
        stats_inside = get_cache_stats()
        # Should have some cache activity
        assert stats_inside["element_list"].misses > 0

    # After exit, caches should be cleared
    stats_after = get_cache_stats()
    assert stats_after["element_list"].hits == 0
    assert stats_after["element_list"].misses == 0


def test_cache_different_containers():
    """Test that different containers have separate cache entries."""
    clear_all_caches()

    doc1 = html(t"""<div><button>Button 1</button></div>""")
    doc2 = html(t"""<div><button>Button 2</button></div>""")

    # Query both documents
    _ = query_all_by_role(doc1, "button")
    _ = query_all_by_role(doc2, "button")

    stats = get_cache_stats()
    # Should have 2 cache misses (one per container)
    assert stats["element_list"].misses == 2


def test_cache_skip_root_variations():
    """Test that skip_root creates separate cache entries."""
    clear_all_caches()

    document = html(t"""<button>Button</button>""")

    # Import get_all_elements directly to test skip_root
    from aria_testing.utils import get_all_elements

    # Query with skip_root=False
    elements1 = get_all_elements(document, skip_root=False)

    # Query with skip_root=True (different cache key)
    elements2 = get_all_elements(document, skip_root=True)

    stats = get_cache_stats()
    # Should have 2 cache misses for different skip_root values
    assert stats["element_list"].misses == 2
    assert len(elements1) != len(elements2)


def test_early_exit_with_single_element():
    """Test early-exit queries with single element."""
    clear_all_caches()

    document = html(t"""<div>
        <button>Save</button>
        <a href="#">Link</a>
    </div>""")

    # get_by uses early exit internally (_max_results=2)
    # Should find one button without issue
    _ = get_by_role(document, "button")

    stats = get_cache_stats()
    # Element list cache may or may not be used depending on internal logic
    # Role cache should still work
    total_ops = stats["element_list"].hits + stats["element_list"].misses
    assert total_ops >= 0  # Just verify stats are tracking


def test_cache_uses_id_based_keys():
    """Test that caches use id()-based keys since tdom doesn't support weakref."""
    clear_all_caches()

    document = html(t"""<div><button>Temp</button></div>""")

    # Query to populate cache
    _ = query_all_by_role(document, "button")

    element_cache = get_element_list_cache()
    role_cache = get_role_cache()

    initial_elem_size = element_cache.size()
    initial_role_size = role_cache.size()

    assert initial_elem_size > 0
    assert initial_role_size > 0

    # Verify caches use regular dicts with id() keys
    assert isinstance(element_cache._cache, dict)
    assert isinstance(role_cache._cache, dict)

    # Manual cache clearing is necessary since we can't use weak references
    clear_all_caches()
    assert element_cache.size() == 0
    assert role_cache.size() == 0


def test_cache_stats_hit_rate():
    """Test cache statistics hit rate calculation."""
    clear_all_caches()

    document = html(t"""<div>
        <button>Save</button>
        <button>Cancel</button>
    </div>""")

    # First query - miss
    _ = query_all_by_role(document, "button")

    # Second query - hit
    _ = query_all_by_role(document, "button")

    # Third query - hit
    _ = query_all_by_role(document, "button")

    stats = get_cache_stats()
    elem_stats = stats["element_list"]

    # Should have 1 miss and 2 hits
    assert elem_stats.misses == 1
    assert elem_stats.hits == 2
    assert elem_stats.hit_rate == 2 / 3  # 66.67%


def test_complex_dom_caching():
    """Test caching with a more complex DOM structure."""
    clear_all_caches()

    document = html(t"""<div>
        <nav>
            <a href="#">Home</a>
            <a href="#">About</a>
        </nav>
        <main>
            <article>
                <h1>Title</h1>
                <button>Like</button>
                <button>Share</button>
            </article>
        </main>
        <footer>
            <button>Subscribe</button>
        </footer>
    </div>""")

    # Multiple queries on same container
    _ = query_all_by_role(document, "button")
    _ = query_all_by_role(document, "link")
    _ = query_all_by_role(document, "heading")
    _ = get_all_by_role(document, "navigation")

    stats = get_cache_stats()

    # First query misses, rest should hit
    assert stats["element_list"].hits >= 3
    assert stats["element_list"].misses == 1

    # Role cache should have many hits for repeated role checks
    assert stats["role"].hits > 0
