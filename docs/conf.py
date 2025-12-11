"""
Sphinx configuration for the aria-testing project.

This configuration uses the Furo theme and MyST-Parser to support Markdown
(`.md`) sources for documentation.
"""

import os
import sys
from datetime import datetime

# -- Project information -----------------------------------------------------

project = "aria-testing"
author = "pauleveritt"
copyright = f"{datetime.now().year}, {author}"

version = "0.0.1"
# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
]

# Recognize Markdown files as sources
source_suffix = {
    ".md": "markdown",
}

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

# Support including external files (e.g., README.md)
myst_parser_include = {
    "relative_docs_path": "../",
}

templates_path = ["_templates"]
exclude_patterns: list[str] = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]


# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]

# If building from within repo, make sure src/ is importable for autodoc, etc.
sys.path.insert(0, os.path.abspath(os.path.join("..", "src")))
