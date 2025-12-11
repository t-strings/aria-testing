"""
Test thread safety and free-threading compatibility.

These tests verify that aria-testing works correctly in multi-threaded environments,
including Python 3.14's free-threaded (no-GIL) mode.
"""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from tdom.processor import html

from aria_testing import (
    get_all_by_role,
    get_by_label_text,
    get_by_role,
    get_by_test_id,
    get_by_text,
    query_all_by_class,
)

# Sample HTML for testing
SAMPLE_HTML = html(
    t"""
<div>
    <header>
        <h1>Test Page</h1>
        <nav>
            <a href="/home">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </nav>
    </header>
    <main>
        <article>
            <h2>Article Title</h2>
            <p>Article content here</p>
        </article>
        <form>
            <label>Email
                <input type="email" name="email" />
            </label>
            <label>Username
                <input type="text" name="username" />
            </label>
            <button type="submit">Submit</button>
            <button type="reset">Reset</button>
        </form>
        <div class="card" data-testid="card-1">Card 1</div>
        <div class="card" data-testid="card-2">Card 2</div>
        <div class="card" data-testid="card-3">Card 3</div>
    </main>
</div>
"""
)


class TestConcurrentQueries:
    """Test that multiple threads can query the same container simultaneously."""

    def test_concurrent_role_queries(self):
        """Multiple threads can query by role simultaneously."""
        results = []
        errors = []

        def query_role(role: str) -> None:
            try:
                elements = get_all_by_role(SAMPLE_HTML, role)
                results.append((role, len(elements)))
            except Exception as e:
                errors.append((role, e))

        # Query different roles from multiple threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            roles = ["link", "button", "heading", "navigation", "textbox"]
            futures = [executor.submit(query_role, role) for role in roles * 20]

            # Wait for all to complete
            for future in as_completed(futures):
                future.result()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors in concurrent queries: {errors}"

        # Verify we got expected number of results
        assert len(results) == 100  # 5 roles * 20 repetitions

        # Verify results are consistent
        link_counts = [count for role, count in results if role == "link"]
        assert all(count == 3 for count in link_counts), "Inconsistent link counts"

        button_counts = [count for role, count in results if role == "button"]
        assert all(count == 2 for count in button_counts), "Inconsistent button counts"

    def test_concurrent_text_queries(self):
        """Multiple threads can query by text simultaneously using query_all."""
        results = []
        errors = []

        def query_article_text() -> None:
            try:
                # Use query_all_by_text which doesn't raise on multiple matches
                from aria_testing import query_all_by_text

                elements = query_all_by_text(SAMPLE_HTML, "Article Title")
                results.append(("Article Title", len(elements)))
            except Exception as e:
                errors.append(("Article Title", e))

        with ThreadPoolExecutor(max_workers=10) as executor:
            # Run the same query 100 times concurrently
            futures = [executor.submit(query_article_text) for _ in range(100)]

            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors in concurrent text queries: {errors}"
        assert len(results) == 100

        # Verify all results are consistent - should find 1 or 2 elements (h2 and potentially parent)
        counts = [count for _, count in results]
        assert all(c > 0 for c in counts), "Should find at least one element"
        assert len(set(counts)) == 1, "Should get consistent count across all queries"

    def test_concurrent_mixed_queries(self):
        """Multiple threads can perform different query types simultaneously."""
        results = []
        errors = []

        def query_1() -> None:
            try:
                links = get_all_by_role(SAMPLE_HTML, "link")
                results.append(("links", len(links)))
            except Exception as e:
                errors.append(("query_1", e))

        def query_2() -> None:
            try:
                button = get_by_role(SAMPLE_HTML, "button", name="Submit")
                results.append(("submit_button", button.attrs.get("type")))
            except Exception as e:
                errors.append(("query_2", e))

        def query_3() -> None:
            try:
                email = get_by_label_text(SAMPLE_HTML, "Email")
                results.append(("email_input", email.attrs.get("type")))
            except Exception as e:
                errors.append(("query_3", e))

        def query_4() -> None:
            try:
                cards = query_all_by_class(SAMPLE_HTML, "card")
                results.append(("cards", len(cards)))
            except Exception as e:
                errors.append(("query_4", e))

        with ThreadPoolExecutor(max_workers=20) as executor:
            # Run different query types concurrently, multiple times
            futures = []
            for _ in range(25):
                futures.append(executor.submit(query_1))
                futures.append(executor.submit(query_2))
                futures.append(executor.submit(query_3))
                futures.append(executor.submit(query_4))

            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors in mixed queries: {errors}"
        assert len(results) == 100

        # Verify all results are consistent
        link_counts = [val for key, val in results if key == "links"]
        assert all(count == 3 for count in link_counts)

        submit_types = [val for key, val in results if key == "submit_button"]
        assert all(t == "submit" for t in submit_types)

        email_types = [val for key, val in results if key == "email_input"]
        assert all(t == "email" for t in email_types)

        card_counts = [val for key, val in results if key == "cards"]
        assert all(count == 3 for count in card_counts)


class TestConcurrentContainers:
    """Test that multiple threads can work with different containers."""

    def test_independent_containers(self):
        """Each thread can work with its own container independently."""
        results = []
        errors = []

        def process_html(thread_id: int) -> None:
            try:
                container = html(t"""<div><h1>Thread {thread_id}</h1></div>""")
                # Verify we can find the heading
                _ = get_by_role(container, "heading", level=1)
                text_content = get_by_text(container, f"Thread {thread_id}")
                results.append((thread_id, text_content.tag))
            except Exception as e:
                errors.append((thread_id, e))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_html, i) for i in range(50)]

            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors processing independent containers: {errors}"
        assert len(results) == 50
        assert all(tag == "h1" for _, tag in results)

    def test_concurrent_container_creation_and_query(self):
        """Threads can create containers and query them concurrently."""
        results = []
        errors = []

        def create_and_query(idx: int) -> None:
            try:
                # Each thread creates its own container
                container = html(
                    t"""
                <div>
                    <button data-testid="btn-{idx}">Button {idx}</button>
                    <a href="/page-{idx}">Link {idx}</a>
                </div>
                """
                )

                # Query the container
                button = get_by_test_id(container, f"btn-{idx}")
                link = get_by_role(container, "link")

                # Get button text and link href
                from aria_testing import get_text_content

                button_text = get_text_content(button)
                href = link.attrs["href"]

                results.append((idx, button_text, href))
            except Exception as e:
                errors.append((idx, e))

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_and_query, i) for i in range(100)]

            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors in container creation: {errors}"
        assert len(results) == 100

        # Verify each thread got its own correct data
        for idx, button_text, href in results:
            assert button_text == f"Button {idx}"
            assert href == f"/page-{idx}"


class TestThreadSafetyStress:
    """Stress tests to verify no race conditions under heavy load."""

    def test_high_concurrency_stress(self):
        """Stress test with many concurrent queries."""
        errors = []
        success_count = 0
        lock = threading.Lock()

        def stress_query() -> None:
            nonlocal success_count
            try:
                # Perform multiple queries
                get_by_role(SAMPLE_HTML, "heading", level=1)
                get_all_by_role(SAMPLE_HTML, "link")
                get_by_role(SAMPLE_HTML, "button", name="Submit")
                query_all_by_class(SAMPLE_HTML, "card")

                with lock:
                    success_count += 1
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=50) as executor:
            # Run 500 concurrent queries
            futures = [executor.submit(stress_query) for _ in range(500)]

            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors under stress: {errors}"
        assert success_count == 500

    def test_repeated_queries_consistency(self):
        """Verify query results are consistent across many iterations."""
        results = {}
        errors = []

        def repeated_query(thread_id: int) -> None:
            try:
                # Each thread performs the same queries multiple times
                for _ in range(100):
                    links = get_all_by_role(SAMPLE_HTML, "link")
                    buttons = get_all_by_role(SAMPLE_HTML, "button")
                    headings = get_all_by_role(SAMPLE_HTML, "heading")

                    # Store counts
                    results[thread_id] = (len(links), len(buttons), len(headings))
            except Exception as e:
                errors.append((thread_id, e))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(repeated_query, i) for i in range(10)]

            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors in repeated queries: {errors}"

        # All threads should get the same counts
        all_results = list(results.values())
        assert len(set(all_results)) == 1, "Inconsistent results across threads"
        assert all_results[0] == (3, 2, 2)  # 3 links, 2 buttons, 2 headings


class TestImmutableDataStructures:
    """Test that module-level data structures remain immutable under concurrent access."""

    def test_role_map_immutability(self):
        """Verify role mappings cannot be modified even under concurrent access."""
        from aria_testing.queries import _INPUT_TYPE_MAP, _ROLE_MAP

        errors = []

        def try_modify_role_map() -> None:
            try:
                # These should all fail due to MappingProxyType
                # Using type: ignore because we're intentionally testing invalid operation
                _ROLE_MAP["test"] = "test"  # type: ignore[index]
                errors.append("Successfully modified _ROLE_MAP (should not happen)")
            except TypeError:
                pass  # Expected

        def try_modify_input_map() -> None:
            try:
                _INPUT_TYPE_MAP["test"] = "test"  # type: ignore[index]
                errors.append(
                    "Successfully modified _INPUT_TYPE_MAP (should not happen)"
                )
            except TypeError:
                pass  # Expected

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for _ in range(100):
                futures.append(executor.submit(try_modify_role_map))
                futures.append(executor.submit(try_modify_input_map))

            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Unexpected modifications: {errors}"

    def test_concurrent_role_lookups(self):
        """Verify role lookups are thread-safe and consistent."""
        from aria_testing.queries import get_role_for_element
        from tdom import Element

        results = []
        errors = []

        def lookup_roles() -> None:
            try:
                # Create test elements
                button_container = html(t"<button>Click me</button>")
                nav_container = html(t"<nav><a href='/'>Home</a></nav>")
                heading_container = html(t"<h1>Title</h1>")

                # Extract Element nodes for role lookup
                button = (
                    button_container if isinstance(button_container, Element) else None
                )
                nav = nav_container if isinstance(nav_container, Element) else None
                heading = (
                    heading_container
                    if isinstance(heading_container, Element)
                    else None
                )

                # Lookup roles
                button_role = get_role_for_element(button) if button else None
                nav_role = get_role_for_element(nav) if nav else None
                heading_role = get_role_for_element(heading) if heading else None

                results.append((button_role, nav_role, heading_role))
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(lookup_roles) for _ in range(100)]

            for future in as_completed(futures):
                future.result()

        assert len(errors) == 0, f"Errors in role lookups: {errors}"

        # All results should be identical
        assert len(set(results)) == 1, "Inconsistent role lookups"
        assert results[0] == ("button", "navigation", "heading")


# Mark all tests to run with pytest-xdist
pytestmark = pytest.mark.usefixtures("_verify_parallel_execution")


@pytest.fixture
def _verify_parallel_execution():
    """Fixture that ensures tests can run in parallel."""
    # This fixture does nothing, but its presence ensures pytest-xdist compatibility
    yield
