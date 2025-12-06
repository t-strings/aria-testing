#!/usr/bin/env python
"""Benchmark caching performance improvements."""

import time

from tdom import html

from aria_testing import (
    CacheContext,
    clear_all_caches,
    get_cache_stats,
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
    # Warmup
    for _ in range(10):
        result = operation()

    start = time.perf_counter()
    for _ in range(iterations):
        result = operation()
        _ = len(result) if isinstance(result, list) else result
    end = time.perf_counter()

    total_time = (end - start) * 1_000_000  # Convert to microseconds
    avg_time = total_time / iterations

    print(f"  {name:<35} {avg_time:>8.3f}μs/op")
    return avg_time


def run_cache_benchmark():
    """Run caching benchmarks."""
    print("=" * 80)
    print("CACHING PERFORMANCE BENCHMARK")
    print("=" * 80)

    print("\nCreating test DOM...")
    dom = create_test_dom()
    print("✓ DOM created\n")

    # Benchmark WITHOUT caching
    print("=" * 80)
    print("WITHOUT CACHING (baseline)")
    print("=" * 80)

    results_no_cache = {}

    with CacheContext(enabled=False):
        results_no_cache["role_link"] = benchmark_operation(
            "query_all_by_role('link')", lambda: query_all_by_role(dom, "link")
        )
        results_no_cache["role_heading"] = benchmark_operation(
            "query_all_by_role('heading')", lambda: query_all_by_role(dom, "heading")
        )
        results_no_cache["text_query"] = benchmark_operation(
            "query_all_by_text('Section 50')",
            lambda: query_all_by_text(dom, "Section 50"),
        )
        results_no_cache["class_query"] = benchmark_operation(
            "query_all_by_class('item')", lambda: query_all_by_class(dom, "item")
        )
        results_no_cache["tag_section"] = benchmark_operation(
            "query_all_by_tag_name('section')",
            lambda: query_all_by_tag_name(dom, "section"),
        )

    avg_no_cache = sum(results_no_cache.values()) / len(results_no_cache)

    # Benchmark WITH caching
    print("\n" + "=" * 80)
    print("WITH CACHING (optimized)")
    print("=" * 80)

    clear_all_caches()
    results_with_cache = {}

    results_with_cache["role_link"] = benchmark_operation(
        "query_all_by_role('link')", lambda: query_all_by_role(dom, "link")
    )
    results_with_cache["role_heading"] = benchmark_operation(
        "query_all_by_role('heading')", lambda: query_all_by_role(dom, "heading")
    )
    results_with_cache["text_query"] = benchmark_operation(
        "query_all_by_text('Section 50')",
        lambda: query_all_by_text(dom, "Section 50"),
    )
    results_with_cache["class_query"] = benchmark_operation(
        "query_all_by_class('item')", lambda: query_all_by_class(dom, "item")
    )
    results_with_cache["tag_section"] = benchmark_operation(
        "query_all_by_tag_name('section')",
        lambda: query_all_by_tag_name(dom, "section"),
    )

    avg_with_cache = sum(results_with_cache.values()) / len(results_with_cache)

    # Calculate improvements
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)

    print(f"\nWithout caching: {avg_no_cache:.3f}μs per query (average)")
    print(f"With caching:    {avg_with_cache:.3f}μs per query (average)")

    improvement = ((avg_no_cache - avg_with_cache) / avg_no_cache) * 100
    speedup = avg_no_cache / avg_with_cache

    print(f"\nImprovement:     {improvement:+.1f}%")
    print(f"Speedup:         {speedup:.2f}x faster")

    # Individual query improvements
    print("\nPer-Query Improvements:")
    print("-" * 80)
    print(f"{'Query':<35} {'No Cache':<12} {'With Cache':<12} {'Speedup':<10}")
    print("-" * 80)

    for key in results_no_cache:
        no_cache_time = results_no_cache[key]
        cache_time = results_with_cache[key]
        query_speedup = no_cache_time / cache_time
        print(
            f"{key:<35} {no_cache_time:>8.3f}μs  {cache_time:>8.3f}μs  {query_speedup:>6.2f}x"
        )

    # Show cache statistics
    print("\n" + "=" * 80)
    print("CACHE STATISTICS")
    print("=" * 80)

    stats = get_cache_stats()
    print(f"\nElement List Cache: {stats['element_list']}")
    print(f"Role Cache:         {stats['role']}")

    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80)


def main():
    """CLI entry point."""
    run_cache_benchmark()


if __name__ == "__main__":
    main()
