#!/usr/bin/env python
"""Quick performance benchmark for regression testing.

Run this before and after optimizations to measure improvements.
"""

import time

from tdom import html

from aria_testing.queries import (
    query_all_by_class,
    query_all_by_role,
    query_all_by_tag_name,
    query_all_by_text,
)


def create_test_dom():
    """Create a medium-sized DOM for benchmarking."""
    sections = "".join(
        f"<section><h2>Section {i}</h2><p>Content {i}</p></section>" for i in range(100)
    )
    nav_links = "".join(f'<a href="/page{i}">Link {i}</a>' for i in range(50))
    list_items = "".join(f'<li class="item">Item {i}</li>' for i in range(50))

    return html(t"""<html>
        <body>
            <nav>{nav_links}</nav>
            <main>{sections}</main>
            <ul>{list_items}</ul>
        </body>
    </html>""")


def benchmark_operation(name: str, operation, iterations: int = 100):
    """Benchmark a single operation."""
    # Warmup to ensure JIT compilation, etc.
    for _ in range(10):
        result = operation()

    start = time.perf_counter()
    for _ in range(iterations):
        result = operation()
        # Prevent optimization by accessing result
        _ = len(result) if isinstance(result, list) else result
    end = time.perf_counter()

    total_time = (end - start) * 1_000_000  # Convert to microseconds
    avg_time = total_time / iterations

    print(f"  {name:<30} {avg_time:>8.3f}μs/op  ({iterations} iterations)")
    return avg_time


def run_benchmark():
    """Run all benchmarks."""
    print("=" * 80)
    print("ARIA-TESTING PERFORMANCE BENCHMARK")
    print("=" * 80)

    print("\nCreating test DOM...")
    dom = create_test_dom()
    print("✓ DOM created\n")

    print("Running benchmarks...")
    print("-" * 80)

    results = {}

    # Role queries
    results["role_link"] = benchmark_operation(
        "query_all_by_role('link')", lambda: query_all_by_role(dom, "link")
    )
    results["role_heading"] = benchmark_operation(
        "query_all_by_role('heading')", lambda: query_all_by_role(dom, "heading")
    )
    results["role_with_name"] = benchmark_operation(
        "query_all_by_role(name filter)",
        lambda: query_all_by_role(dom, "heading", name="Section 50"),
    )

    # Text queries
    results["text_query"] = benchmark_operation(
        "query_all_by_text('Section 50')",
        lambda: query_all_by_text(dom, "Section 50"),
    )

    # Class queries
    results["class_query"] = benchmark_operation(
        "query_all_by_class('item')", lambda: query_all_by_class(dom, "item")
    )

    # Tag queries
    results["tag_section"] = benchmark_operation(
        "query_all_by_tag_name('section')",
        lambda: query_all_by_tag_name(dom, "section"),
    )
    results["tag_a"] = benchmark_operation(
        "query_all_by_tag_name('a')", lambda: query_all_by_tag_name(dom, "a")
    )

    print("-" * 80)
    print(f"\nAverage time per query: {sum(results.values()) / len(results):.3f}μs")
    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80)

    # Performance targets
    print("\nPerformance Targets:")
    avg_time = sum(results.values()) / len(results)
    if avg_time < 30:
        print("  ✓ EXCELLENT - Queries are very fast")
    elif avg_time < 50:
        print("  ✓ GOOD - Performance is acceptable")
    elif avg_time < 100:
        print("  ⚠ FAIR - Consider optimization")
    else:
        print("  ✗ SLOW - Optimization recommended")

    print(
        f"\n  Current: {avg_time:.1f}μs/query | Target: <50μs/query | Best: <30μs/query"
    )


def main():
    """CLI entry point."""
    run_benchmark()


if __name__ == "__main__":
    main()
