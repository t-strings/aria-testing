#!/usr/bin/env python
"""Profile the test suite to identify performance bottlenecks.

Uses cProfile for CPU profiling and provides detailed stats.
"""

import cProfile
import pstats
from io import StringIO


def run_tests_for_profiling():
    """Run tests programmatically for profiling."""
    import pytest

    # Run tests with minimal output
    pytest.main(
        [
            "tests/",
            "-v",
            "--tb=short",
            "-p",
            "no:warnings",
        ]
    )


def profile_tests():
    """Profile test execution and display results."""
    profiler = cProfile.Profile()

    print("=" * 80)
    print("Starting profiling of test suite...")
    print("=" * 80)

    # Profile the test run
    profiler.enable()
    run_tests_for_profiling()
    profiler.disable()

    # Create stats object
    stats = pstats.Stats(profiler)

    # Sort by cumulative time
    print("\n" + "=" * 80)
    print("TOP 30 FUNCTIONS BY CUMULATIVE TIME")
    print("=" * 80)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(30)

    # Sort by time spent in function (not including subcalls)
    print("\n" + "=" * 80)
    print("TOP 30 FUNCTIONS BY INTERNAL TIME")
    print("=" * 80)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats(30)

    # Show callers for the most time-consuming functions
    print("\n" + "=" * 80)
    print("CALLERS OF MOST EXPENSIVE FUNCTIONS")
    print("=" * 80)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_callers(10)

    # Save detailed stats to file
    output_file = "profile_stats.txt"
    with open(output_file, "w") as f:
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats()
        f.write(stream.getvalue())

    print(f"\n\nDetailed stats saved to: {output_file}")

    # Save profile data for visualization tools
    profiler.dump_stats("profile_data.prof")
    print("Profile data saved to: profile_data.prof")
    print("\nYou can visualize this with: snakeviz profile_data.prof")
    print("(Install with: uv pip install snakeviz)")


if __name__ == "__main__":
    profile_tests()
