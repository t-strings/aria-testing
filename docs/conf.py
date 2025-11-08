"""
Sphinx configuration for the aria-testing project.

This configuration uses the Furo theme and MyST-Parser to support Markdown
(`.md`) sources for documentation.
"""

import os
import sys
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version

# -- Project information -----------------------------------------------------

project = "aria-testing"
author = "pauleveritt"
copyright = f"{datetime.now().year}, {author}"

release = version(project)

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
    "linkify",
]

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
