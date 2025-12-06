#!/usr/bin/env python
"""Profile the queries module directly with synthetic workload.

This creates a realistic DOM tree and profiles query operations.
"""

import cProfile
import pstats

from tdom import html

from aria_testing.queries import (
    query_all_by_class,
    query_all_by_role,
    query_all_by_tag_name,
    query_all_by_text,
    query_by_role,
)


def create_large_dom():
    """Create a large, realistic DOM for testing."""
    # Pre-generate the HTML parts
    nav_links = "".join(f'<a href="/page{i}">Link {i}</a>' for i in range(50))
    sections = "".join(
        f"<section><h2>Section {i}</h2><p>Content {i}</p></section>" for i in range(100)
    )
    form_inputs = "".join(
        f"""<div class="form-group">
            <label for="input{i}">Label {i}</label>
            <input type="text" id="input{i}" data-testid="test-{i}"/>
        </div>"""
        for i in range(50)
    )
    footer_items = "".join(
        f'<li class="footer-item">Footer item {i}</li>' for i in range(30)
    )

    # Use t-string syntax properly
    return html(t"""<html>
        <head><title>Test Page</title></head>
        <body>
            <header role="banner">
                <nav>{nav_links}</nav>
            </header>
            <main>
                <article>
                    <h1>Main Heading</h1>
                    <p>Paragraph text content here</p>
                    {sections}
                </article>
                <form>
                    {form_inputs}
                    <button type="submit">Submit</button>
                </form>
            </main>
            <footer role="contentinfo">
                <ul>{footer_items}</ul>
            </footer>
        </body>
    </html>""")


def benchmark_queries(dom):
    """Run various query operations on the DOM."""
    # Role queries - most common operation
    for _ in range(100):
        _ = query_all_by_role(dom, "link")
        _ = query_all_by_role(dom, "button")
        _ = query_all_by_role(dom, "heading")
        _ = query_all_by_role(dom, "textbox")

    # Text queries
    for i in range(50):
        _ = query_all_by_text(dom, f"Section {i}")
        _ = query_all_by_text(dom, f"Content {i}")

    # Class queries
    for _ in range(50):
        _ = query_all_by_class(dom, "form-group")
        _ = query_all_by_class(dom, "footer-item")

    # Tag queries
    for _ in range(50):
        _ = query_all_by_tag_name(dom, "section")
        _ = query_all_by_tag_name(dom, "input")
        _ = query_all_by_tag_name(dom, "p")

    # Complex role queries with name - expensive
    for i in range(25):
        _ = query_all_by_role(dom, "heading", name=f"Section {i}")

    # Get operations that need unique match
    _ = query_by_role(dom, "banner")


def profile_queries():
    """Profile query operations."""
    print("=" * 80)
    print("Creating test DOM...")
    print("=" * 80)

    dom = create_large_dom()
    print("DOM created successfully")

    print("\n" + "=" * 80)
    print("Starting profiling of query operations...")
    print("=" * 80)

    profiler = cProfile.Profile()
    profiler.enable()
    benchmark_queries(dom)
    profiler.disable()

    # Create stats object
    stats = pstats.Stats(profiler)

    # Sort by cumulative time
    print("\n" + "=" * 80)
    print("TOP 40 FUNCTIONS BY CUMULATIVE TIME")
    print("=" * 80)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(40)

    # Sort by time spent in function (not including subcalls)
    print("\n" + "=" * 80)
    print("TOP 40 FUNCTIONS BY INTERNAL TIME")
    print("=" * 80)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats(40)

    # Show functions from our module only
    print("\n" + "=" * 80)
    print("ARIA-TESTING MODULE FUNCTIONS")
    print("=" * 80)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats("aria_testing")

    # Save stats
    output_file = "profile_queries_stats.txt"
    with open(output_file, "w") as f:
        from io import StringIO

        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats()
        f.write(stream.getvalue())

    print(f"\n\nDetailed stats saved to: {output_file}")

    profiler.dump_stats("profile_queries_data.prof")
    print("Profile data saved to: profile_queries_data.prof")
    print("\nVisualize with: snakeviz profile_queries_data.prof")


if __name__ == "__main__":
    profile_queries()
