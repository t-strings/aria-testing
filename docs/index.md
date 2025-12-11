# aria-testing

```{include} ../README.md
:start-after: aria-testing
:relative-docs: docs/
:relative-images:
```

## Documentation Guide

This documentation is organized into focused sections for different needs:

### Getting Started

Start here if you're new to aria-testing:

- **README** (above) - Quick start and overview
- **[Query Reference](queries.md)** - All query types and their usage
- **[Assertion Helpers](assertion-helpers.md)** - Deferred execution for dynamic testing systems

### Practical Guides

Learn by example:

- **[Examples](examples.md)** - Real-world testing patterns and use cases
- **[Best Practices](best-practices.md)** - Guidelines for writing effective, accessible tests

### Reference

Complete API documentation:

- **[API Reference](api.md)** - Full function signatures, parameters, and return types

### Advanced Topics

Deep dives for advanced users and contributors:

- **[Architecture](architecture.md)** - System design, query factory pattern, role mapping
- **[Performance](performance.md)** - Optimization strategies, benchmarks, caching details
- **[Contributing](contributing.md)** - Development setup, code standards, how to contribute

## Quick Links

- 📦 [PyPI Package](https://pypi.org/project/aria-testing/)
- 🐙 [GitHub Repository](https://github.com/t-strings/aria-testing)
- 🐛 [Report Issues](https://github.com/t-strings/aria-testing/issues)
- 💬 [Discussions](https://github.com/t-strings/aria-testing/discussions)

## Philosophy

aria-testing follows the [DOM Testing Library](https://testing-library.com/docs/dom-testing-library/intro) philosophy:

> **"The more your tests resemble the way your software is used, the more confidence they can give you."**

This means:

- ✅ **Query by role** (how screen readers see your app)
- ✅ **Query by label text** (how users identify form fields)
- ✅ **Query by text** (what users see)
- ❌ Avoid querying by test IDs, CSS classes, or implementation details

## Project Info

- **License**: MIT
- **Python**: 3.14+
- **Dependencies**: tdom

```{toctree}
:maxdepth: 2
:hidden:

queries
assertion-helpers
examples
best-practices
api
architecture
performance
contributing
```
