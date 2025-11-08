"""
Tests for implicit ARIA roles with type hints.
"""

import pytest
from tdom.processor import html

from aria_testing import get_by_role


@pytest.fixture
def simple_document():
    """Create a simple document structure."""
    return html(t"""<div>
        <nav>Navigation</nav>
        <main>Main content</main>
        <button>Click me</button>
        <h1>Title</h1>
    </div>""")


def test_landmark_roles(simple_document):
    """Test landmark role type hints work."""
    nav = get_by_role(simple_document, "navigation")
    assert nav.tag == "nav"

    main = get_by_role(simple_document, "main")
    assert main.tag == "main"


def test_widget_roles(simple_document):
    """Test widget role type hints work."""
    button = get_by_role(simple_document, "button")
    assert button.tag == "button"


def test_document_structure_roles(simple_document):
    """Test document structure role type hints work."""
    heading = get_by_role(simple_document, "heading")
    assert heading.tag == "h1"


def test_type_checking_example():
    """Demonstrate type checking works for role parameters."""
    doc = html(t"<div><nav>Navigation</nav></div>")

    # These should all work with proper type hints
    nav1 = get_by_role(doc, "navigation")  # Literal string

    # Type annotations should prevent invalid roles at type-check time
    assert nav1.tag == "nav"
