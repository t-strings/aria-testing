"""
Tests for aria_testing.queries module.
"""

import pytest
from tdom.processor import html

from aria_testing.errors import ElementNotFoundError, MultipleElementsError
from aria_testing.queries import (
    get_all_by_class,
    get_all_by_label_text,
    get_all_by_role,
    get_all_by_tag_name,
    get_all_by_test_id,
    get_all_by_text,
    get_by_class,
    get_by_id,
    get_by_label_text,
    get_by_role,
    get_by_tag_name,
    get_by_test_id,
    get_by_text,
    get_role_for_element,
    query_all_by_class,
    query_all_by_label_text,
    query_all_by_role,
    query_all_by_tag_name,
    query_all_by_test_id,
    query_all_by_text,
    query_by_class,
    query_by_id,
    query_by_label_text,
    query_by_role,
    query_by_tag_name,
    query_by_test_id,
    query_by_text,
)
from aria_testing.utils import get_text_content


@pytest.fixture
def sample_document():
    """Create a sample document structure for testing."""
    return html(t"""<div>
        <h1>Welcome</h1>
        <p>Hello world</p>
        <button>Click me</button>
        <input type="text" placeholder="Enter name" />
        <div data-testid="content">
            Main content
            <span>nested</span>
        </div>
        <button data-testid="save">Save</button>
        <button data-testid="cancel">Cancel</button>
    </div>""")


def test_query_by_text_exact_match(sample_document):
    element = query_by_text(sample_document, "Hello world")
    assert element is not None
    assert element.tag == "p"


def test_query_by_text_not_found(sample_document):
    element = query_by_text(sample_document, "Not found")
    assert element is None


# Note: substring and regex matching not implemented yet
# def test_query_by_text_substring(sample_document):
#     element = query_by_text(sample_document, "Hello", exact=False)
#     assert element is not None
#     assert element.tag == "p"
#
#
# def test_query_by_text_regex(sample_document):
#     pattern = re.compile(r"Click.*")
#     element = query_by_text(sample_document, pattern)
#     assert element is not None
#     assert element.tag == "button"


def test_get_by_text_success(sample_document):
    element = get_by_text(sample_document, "Welcome")
    assert element.tag == "h1"


def test_get_by_text_not_found(sample_document):
    with pytest.raises(ElementNotFoundError) as exc_info:
        get_by_text(sample_document, "Not found")
    assert "Unable to find element with text: Not found" in str(exc_info.value)


def test_get_by_text_multiple_elements():
    container = html(t"""<div>
        <p>duplicate</p>
        <span>duplicate</span>
    </div>""")

    with pytest.raises(MultipleElementsError) as exc_info:
        get_by_text(container, "duplicate")
    assert "Found multiple elements with text: duplicate" in str(exc_info.value)
    # Add type checking for MultipleElementsError instance
    assert isinstance(exc_info.value, MultipleElementsError)
    assert exc_info.value.count == 2


def test_query_all_by_text():
    container = html(t"""<div>
        <p>test</p>
        <span>test</span>
        <div>other</div>
    </div>""")

    elements = query_all_by_text(container, "test")
    assert len(elements) == 2
    assert elements[0].tag == "p"
    assert elements[1].tag == "span"


def test_get_all_by_text_success():
    container = html(t"""<div>
        <p>item</p>
        <span>item</span>
    </div>""")

    elements = get_all_by_text(container, "item")
    assert len(elements) == 2


def test_get_all_by_text_not_found(sample_document):
    with pytest.raises(ElementNotFoundError):
        get_all_by_text(sample_document, "Not found")


def test_query_by_test_id_found(sample_document):
    element = query_by_test_id(sample_document, "content")
    assert element is not None
    assert element.attrs["data-testid"] == "content"


def test_query_by_test_id_not_found(sample_document):
    element = query_by_test_id(sample_document, "nonexistent")
    assert element is None


def test_get_by_test_id_success(sample_document):
    element = get_by_test_id(sample_document, "save")
    assert element.attrs["data-testid"] == "save"


def test_get_by_test_id_not_found(sample_document):
    with pytest.raises(ElementNotFoundError) as exc_info:
        get_by_test_id(sample_document, "nonexistent")
    assert "Unable to find element with data-testid: nonexistent" in str(exc_info.value)


def test_get_by_test_id_multiple_elements():
    container = html(t"""<div>
        <button data-testid="action">Button</button>
        <div data-testid="action">Div</div>
    </div>""")

    with pytest.raises(MultipleElementsError):
        get_by_test_id(container, "action")


def test_custom_test_id_attribute():
    container = html(t'<div><button data-qa="submit">Submit</button></div>')

    element = query_by_test_id(container, "submit", attribute="data-qa")
    assert element is not None


def test_query_all_by_test_id():
    container = html(t"""<div>
        <button data-testid="btn">Button</button>
        <input data-testid="btn" type="text" />
    </div>""")

    elements = query_all_by_test_id(container, "btn")
    assert len(elements) == 2


def test_get_all_by_test_id_success():
    container = html(t"""<div>
        <button data-testid="item">Button</button>
        <div data-testid="item">Div</div>
    </div>""")

    elements = get_all_by_test_id(container, "item")
    assert len(elements) == 2


def test_get_all_by_test_id_not_found(sample_document):
    with pytest.raises(ElementNotFoundError):
        get_all_by_test_id(sample_document, "nonexistent")


def test_explicit_role():
    container = html(t'<div><div role="button">Custom button</div></div>')

    element = query_by_role(container, "button")
    assert element is not None


def test_implicit_role_button():
    container = html(t"<div><button>Click me</button></div>")

    element = query_by_role(container, "button")
    assert element is not None
    assert element.tag == "button"


def test_implicit_role_heading():
    container = html(t"""<div>
        <h1>Title</h1>
        <h2>Subtitle</h2>
    </div>""")

    elements = query_all_by_role(container, "heading")
    assert len(elements) == 2


def test_heading_with_level():
    container = html(t"""<div>
        <h1>Title</h1>
        <h2>Subtitle</h2>
    </div>""")

    element = query_by_role(container, "heading", level=1)
    assert element is not None
    assert element.tag == "h1"

    element = query_by_role(container, "heading", level=3)
    assert element is None


def test_aria_level_attribute():
    container = html(
        t'<div><div role="heading" aria-level="3">Custom heading</div></div>'
    )

    element = query_by_role(container, "heading", level=3)
    assert element is not None


def test_input_type_roles():
    container = html(t"""<div>
        <input type="text" />
        <input type="checkbox" />
        <input type="button" />
    </div>""")

    textbox = query_by_role(container, "textbox")
    assert textbox is not None
    assert textbox.attrs["type"] == "text"

    checkbox = query_by_role(container, "checkbox")
    assert checkbox is not None
    assert checkbox.attrs["type"] == "checkbox"

    button = query_by_role(container, "button")
    assert button is not None
    assert button.attrs["type"] == "button"


# Note: Role with name parameter not fully implemented yet
# def test_role_with_name():
#     container = html(t"""<div>
#         <button aria-label="Save container">Save</button>
#         <button aria-label="Cancel operation">Cancel</button>
#     </div>""")
#
#     element = query_by_role(container, "button", name="Save")
#     assert element is not None
#     aria_label = element.attrs.get("aria-label")
#     assert aria_label is not None and "Save" in aria_label


def test_get_by_role_success():
    container = html(t"<div><nav>Navigation</nav></div>")

    element = get_by_role(container, "navigation")
    assert element.tag == "nav"


def test_get_by_role_not_found():
    container = html(t"<div><p>Just text</p></div>")

    with pytest.raises(ElementNotFoundError) as exc_info:
        get_by_role(container, "button")
    assert "Unable to find element with role 'button'" in str(exc_info.value)


def test_get_by_role_multiple_elements():
    container = html(t"""<div>
        <button>First</button>
        <button>Second</button>
    </div>""")

    with pytest.raises(MultipleElementsError):
        get_by_role(container, "button")


def test_get_all_by_role_success():
    container = html(t"""<div>
        <li>Item 1</li>
        <li>Item 2</li>
    </div>""")

    elements = get_all_by_role(container, "listitem")
    assert len(elements) == 2


def test_get_all_by_role_not_found():
    container = html(t"<div><p>Just text</p></div>")

    with pytest.raises(ElementNotFoundError):
        get_all_by_role(container, "button")


def test_get_role_for_element_explicit():
    element = html(t'<div role="button">Button</div>')
    assert get_role_for_element(element) == "button"


def test_get_role_for_element_implicit_button():
    element = html(t"<button>Click</button>")
    assert get_role_for_element(element) == "button"


def test_get_role_for_element_implicit_heading():
    element = html(t"<h1>Title</h1>")
    assert get_role_for_element(element) == "heading"


def test_get_role_for_element_input_types():
    text_input = html(t'<input type="text" />')
    assert get_role_for_element(text_input) == "textbox"

    checkbox = html(t'<input type="checkbox" />')
    assert get_role_for_element(checkbox) == "checkbox"

    button_input = html(t'<input type="button" />')
    assert get_role_for_element(button_input) == "button"


def test_get_role_for_element_no_role():
    element = html(t"<div>Content</div>")
    assert get_role_for_element(element) is None


def test_get_role_for_element_non_element():
    """Test that get_role_for_element handles non-Element nodes gracefully."""
    from tdom import Text

    # Text nodes don't have roles
    text_node = Text("Just text")
    assert get_role_for_element(text_node) is None

    # Fragments don't have roles
    fragment = html(t"<span>One</span><span>Two</span>")
    assert get_role_for_element(fragment) is None


# Note: _get_accessible_name function not implemented yet
# def test_get_accessible_name_aria_label():
#     element = html(t'<button aria-label="Close dialog">X</button>')
#     assert _get_accessible_name(element) == "Close dialog"
#
#
# def test_get_accessible_name_text_content():
#     element = html(t"<button>Submit form</button>")
#     assert _get_accessible_name(element) == "Submit form"
#
#
# def test_get_accessible_name_empty():
#     element = html(t"<div></div>")
#     assert _get_accessible_name(element) == ""


def test_nested_text_content():
    container = html(t"<div><p>Hello <strong>bold</strong> world</p></div>")

    element = query_by_text(container, "Hello bold world")
    assert element is not None
    assert element.tag == "p"


def test_multiple_query_methods_same_element():
    container = html(
        t'<div><button data-testid="submit" aria-label="Submit form">Submit</button></div>'
    )

    # Should find the same element via different methods
    by_text = query_by_text(container, "Submit")
    by_test_id = query_by_test_id(container, "submit")
    by_role = query_by_role(container, "button")

    assert by_text is by_test_id is by_role


def test_fragment_as_container():
    fragment = html(t"<div>First</div><span>Second</span>")

    element = query_by_text(fragment, "First")
    assert element is not None
    assert element.tag == "div"

    elements = query_all_by_text(fragment, "First")
    assert len(elements) == 1


# ===== Name Matching Tests =====


def test_role_with_name_text_content():
    """Test name matching using text content."""
    container = html(t"""<div>
        <button>Save Document</button>
        <button>Cancel Operation</button>
        <button>Delete File</button>
    </div>""")

    # Test substring matching
    element = query_by_role(container, "button", name="Save")
    assert element is not None
    assert "Save Document" in get_text_content(element)

    element = query_by_role(container, "button", name="Cancel")
    assert element is not None
    assert "Cancel Operation" in get_text_content(element)

    # Test full text matching
    element = query_by_role(container, "button", name="Delete File")
    assert element is not None
    assert "Delete File" in get_text_content(element)


def test_role_with_name_aria_label():
    """Test name matching using aria-label."""
    container = html(t"""<div>
        <button aria-label="Save container">💾</button>
        <button aria-label="Cancel operation">❌</button>
        <button aria-label="Delete file">🗑️</button>
    </div>""")

    element = query_by_role(container, "button", name="Save")
    assert element is not None
    assert element.attrs["aria-label"] == "Save container"

    element = query_by_role(container, "button", name="Cancel")
    assert element is not None
    assert element.attrs["aria-label"] == "Cancel operation"


def test_role_with_name_link_text():
    """Test name matching for links using text content."""
    container = html(t"""<div>
        <a href="/docs">Documentation</a>
        <a href="/about">About Us</a>
        <a href="/contact">Contact</a>
    </div>""")

    element = query_by_role(container, "link", name="Documentation")
    assert element is not None
    assert element.attrs["href"] == "/docs"

    element = query_by_role(container, "link", name="About")
    assert element is not None
    assert element.attrs["href"] == "/about"


def test_role_with_name_image_alt():
    """Test name matching for images using alt text."""
    container = html(t"""<div>
        <img src="logo.png" alt="Company Logo" />
        <img src="avatar.jpg" alt="User Avatar" />
        <img src="icon.svg" alt="Settings Icon" />
    </div>""")

    element = query_by_role(container, "img", name="Company")
    assert element is not None
    assert element.attrs["alt"] == "Company Logo"

    element = query_by_role(container, "img", name="Avatar")
    assert element is not None
    assert element.attrs["alt"] == "User Avatar"

    element = query_by_role(container, "img", name="Settings")
    assert element is not None
    assert element.attrs["alt"] == "Settings Icon"


def test_role_with_name_not_found():
    """Test name matching when no element matches."""
    container = html(t"""<div>
        <button>Save</button>
        <button>Cancel</button>
    </div>""")

    element = query_by_role(container, "button", name="Delete")
    assert element is None


def test_role_with_keyword_arguments():
    """Test using keyword arguments with * separator."""
    container = html(t"""<div>
        <h1>Main Title</h1>
        <h2>Subtitle</h2>
        <button>Save Changes</button>
        <button aria-label="Cancel operation">Cancel</button>
    </div>""")

    # Test with keyword arguments
    element = query_by_role(container, "heading", level=1)
    assert element is not None
    assert element.tag == "h1"

    element = query_by_role(container, "button", name="Save")
    assert element is not None
    assert "Save Changes" in get_text_content(element)

    element = query_by_role(container, "button", name="Cancel")
    assert element is not None
    assert element.attrs["aria-label"] == "Cancel operation"


def test_get_all_by_role_with_name():
    """Test get_all_by_role with name filtering."""
    container = html(t"""<div>
        <button>Save File</button>
        <button>Save As</button>
        <button>Cancel</button>
        <button>Delete File</button>
    </div>""")

    elements = get_all_by_role(container, "button", name="Save")
    assert len(elements) == 2

    # Both buttons should contain "Save" in their accessible name
    for element in elements:
        text = get_text_content(element)
        assert "Save" in text


def test_accessible_name_priority():
    """Test that aria-label takes priority over text content."""
    container = html(t"""<div>
        <button aria-label="Custom Label">Visible Text</button>
    </div>""")

    # Should match aria-label, not text content
    element = query_by_role(container, "button", name="Custom")
    assert element is not None

    # Should not match text content when aria-label is present
    element = query_by_role(container, "button", name="Visible")
    assert element is None


def test_form_controls_name_matching():
    """Test name matching for form controls."""
    container = html(t"""<div>
        <input type="text" placeholder="Enter your name" />
        <input type="email" value="test@example.com" />
        <textarea aria-label="Comments">Default text</textarea>
    </div>""")

    # Match by placeholder
    element = query_by_role(container, "textbox", name="Enter")
    assert element is not None
    assert element.attrs["placeholder"] == "Enter your name"

    # Match by value
    element = query_by_role(container, "textbox", name="test@")
    assert element is not None
    assert element.attrs["value"] == "test@example.com"

    # Match by aria-label (should take priority)
    element = query_by_role(container, "textbox", name="Comments")
    assert element is not None
    assert element.attrs["aria-label"] == "Comments"


# ===== Link Href Support Tests =====


def test_link_name_includes_href():
    """Test that link names include href for comprehensive matching."""
    container = html(t"""<div>
        <a href="/docs">Documentation</a>
        <a href="/api/v1">API Reference</a>
        <a href="https://example.com">External Link</a>
    </div>""")

    # Match by href path
    element = query_by_role(container, "link", name="/docs")
    assert element is not None
    assert element.attrs["href"] == "/docs"

    # Match by href with version
    element = query_by_role(container, "link", name="v1")
    assert element is not None
    assert element.attrs["href"] == "/api/v1"

    # Match by domain in href
    element = query_by_role(container, "link", name="example.com")
    assert element is not None
    assert element.attrs["href"] == "https://example.com"


def test_link_name_text_and_href_combined():
    """Test that both text content and href are searchable for links."""
    container = html(t"""<div>
        <a href="/download">Download Now</a>
        <a href="/signup">Join Today</a>
        <a href="/admin/users">User Management</a>
    </div>""")

    # Match by text content
    element = query_by_role(container, "link", name="Download")
    assert element is not None
    assert "Download Now" in get_text_content(element)

    # Match by href path
    element = query_by_role(container, "link", name="/signup")
    assert element is not None
    assert element.attrs["href"] == "/signup"

    # Match by part of href path
    element = query_by_role(container, "link", name="admin")
    assert element is not None
    assert element.attrs["href"] == "/admin/users"

    # Match by text content when href doesn't contain the term
    element = query_by_role(container, "link", name="Join")
    assert element is not None
    assert "Join Today" in get_text_content(element)


def test_link_href_only_no_text():
    """Test links with href but no text content."""
    container = html(t"""<div>
        <a href="/home" aria-label="Home Page"></a>
        <a href="/search"><img src="search.png" alt="Search" /></a>
        <a href="/profile">👤</a>
    </div>""")

    # Should match by aria-label, not href (aria-label takes priority)
    element = query_by_role(container, "link", name="Home Page")
    assert element is not None
    assert element.attrs["href"] == "/home"

    # Match by href when containing images (no aria-label)
    element = query_by_role(container, "link", name="/search")
    assert element is not None
    assert element.attrs["href"] == "/search"

    # Match by href when containing emoji/unicode (no aria-label)
    element = query_by_role(container, "link", name="/profile")
    assert element is not None
    assert element.attrs["href"] == "/profile"


def test_link_complex_href_patterns():
    """Test complex href patterns and matching."""
    container = html(t"""<div>
        <a href="https://api.github.com/repos/user/repo">GitHub API</a>
        <a href="mailto:contact@example.com">Contact Us</a>
        <a href="tel:+1-555-123-4567">Call Now</a>
        <a href="#section-1">Jump to Section</a>
        <a href="?page=2&sort=name">Next Page</a>
    </div>""")

    # Match by domain in URL
    element = query_by_role(container, "link", name="github.com")
    assert element is not None
    href = element.attrs.get("href", "")
    assert href is not None and "api.github.com" in href

    # Match by email protocol and domain
    element = query_by_role(container, "link", name="mailto:")
    assert element is not None
    assert element.attrs["href"] == "mailto:contact@example.com"

    element = query_by_role(container, "link", name="example.com")
    assert element is not None
    href = element.attrs.get("href", "")
    assert href is not None and "contact@example.com" in href

    # Match by phone protocol
    element = query_by_role(container, "link", name="tel:")
    assert element is not None
    assert element.attrs["href"] == "tel:+1-555-123-4567"

    # Match by phone number part
    element = query_by_role(container, "link", name="555")
    assert element is not None
    href = element.attrs.get("href", "")
    assert href is not None and "555" in href

    # Match by fragment identifier
    element = query_by_role(container, "link", name="#section")
    assert element is not None
    assert element.attrs["href"] == "#section-1"

    # Match by query parameters
    element = query_by_role(container, "link", name="page=2")
    assert element is not None
    href = element.attrs.get("href", "")
    assert href is not None and "page=2" in href


def test_link_priority_aria_label_over_href():
    """Test that aria-label takes priority over href and text for links."""
    container = html(t"""<div>
        <a href="/secret-path" aria-label="Public Label">Hidden Text</a>
    </div>""")

    # Should match aria-label, not href or text
    element = query_by_role(container, "link", name="Public")
    assert element is not None
    assert element.attrs["aria-label"] == "Public Label"

    # Should not match href when aria-label is present
    element = query_by_role(container, "link", name="secret")
    assert element is None

    # Should not match text content when aria-label is present
    element = query_by_role(container, "link", name="Hidden")
    assert element is None


def test_multiple_links_href_matching():
    """Test finding specific links among multiple similar ones using href."""
    container = html(t"""<div>
        <a href="/docs/getting-started">Getting Started</a>
        <a href="/docs/api">API Documentation</a>
        <a href="/docs/examples">Code Examples</a>
        <a href="/blog/getting-started">Blog: Getting Started</a>
    </div>""")

    # Should find the docs version, not the blog version
    element = query_by_role(container, "link", name="/docs/getting")
    assert element is not None
    href = element.attrs.get("href", "")
    assert href is not None and "/docs/getting-started" in href

    # Should find the API docs specifically
    element = query_by_role(container, "link", name="docs/api")
    assert element is not None
    assert element.attrs["href"] == "/docs/api"

    # Should distinguish between docs and blog by path
    element = query_by_role(container, "link", name="/blog/")
    assert element is not None
    href = element.attrs.get("href", "")
    assert href is not None and "/blog/" in href

    # Get all docs links
    elements = get_all_by_role(container, "link", name="/docs/")
    assert len(elements) == 3
    for element in elements:
        href = element.attrs.get("href", "")
        assert href is not None and "/docs/" in href


def test_regex_name_matching():
    """Test regex pattern matching for accessible names."""
    import re

    container = html(t"""<div>
        <button>Save Document</button>
        <button>CANCEL OPERATION</button>
        <button>Delete File</button>
        <a href="/API">API Reference</a>
        <a href="/docs">DOCUMENTATION</a>
    </div>""")

    # Case-insensitive regex for button text
    save_btn = query_by_role(
        container, "button", name=re.compile(r"save", re.IGNORECASE)
    )
    assert save_btn is not None
    assert "Save Document" in get_text_content(save_btn)

    # Regex to match all-caps text
    cancel_btn = query_by_role(container, "button", name=re.compile(r"^[A-Z\s]+$"))
    assert cancel_btn is not None
    assert "CANCEL OPERATION" in get_text_content(cancel_btn)

    # Regex for links with case-insensitive matching
    api_link = query_by_role(container, "link", name=re.compile(r"api", re.IGNORECASE))
    assert api_link is not None
    assert api_link.attrs["href"] == "/API"

    # Get all buttons and links with all-caps names
    caps_buttons = query_all_by_role(
        container, "button", name=re.compile(r"^[A-Z\s]+$")
    )
    # Links have format "TEXT /href" so pattern needs to account for href part
    caps_links = query_all_by_role(
        container, "link", name=re.compile(r"^[A-Z\s]+/[A-Za-z]+$")
    )
    assert len(caps_buttons) == 1  # CANCEL OPERATION
    assert len(caps_links) == 1  # DOCUMENTATION /docs


def test_regex_vs_string_matching():
    """Test that regex and string matching work differently."""
    import re

    container = html(t"""<div>
        <button>save file</button>
        <button>SAVE FILE</button>
        <button>Save Document</button>
    </div>""")

    # String matching is case-sensitive substring
    element = query_by_role(container, "button", name="save")
    assert element is not None
    assert "save file" in get_text_content(element)

    # Regex matching with case-insensitive flag matches all
    elements = get_all_by_role(
        container, "button", name=re.compile(r"save", re.IGNORECASE)
    )
    assert len(elements) == 3

    # Regex for exact word boundaries
    element = query_by_role(
        container, "button", name=re.compile(r"^save file$", re.IGNORECASE)
    )
    assert element is not None
    # Should match the lowercase one first
    text = get_text_content(element) if element.children else ""
    assert text in ["save file", "SAVE FILE"]


def test_regex_with_href_matching():
    """Test regex patterns work with href + text combination for links."""
    import re

    container = html(t"""<div>
        <a href="/api/v1">API v1</a>
        <a href="/api/v2">API v2</a>
        <a href="/docs/api">API Guide</a>
        <a href="/blog">Blog Posts</a>
    </div>""")

    # Regex to match API version links (href contains /api/v)
    api_version_elements = get_all_by_role(
        container, "link", name=re.compile(r"/api/v\d+")
    )
    assert len(api_version_elements) == 2

    # Regex case-insensitive matching for "api" in either text or href
    all_api_elements = get_all_by_role(
        container, "link", name=re.compile(r"api", re.IGNORECASE)
    )
    assert len(all_api_elements) == 3  # All three API-related links

    # Regex for specific version
    v2_element = query_by_role(container, "link", name=re.compile(r"v2"))
    assert v2_element is not None
    assert v2_element.attrs["href"] == "/api/v2"


def test_summary_element_has_button_role():
    """Test that <summary> elements are recognized as having button role."""
    container = html(
        t"""
    <details>
        <summary>Click to expand</summary>
        <p>Hidden content</p>
    </details>
    """
    )

    # Should be able to find summary by button role
    button = get_by_role(container, "button")
    assert button is not None
    assert button.tag == "summary"
    assert get_text_content(button) == "Click to expand"


def test_summary_element_button_role_with_name():
    """Test finding <summary> elements by button role with accessible name."""
    container = html(
        t"""
    <details>
        <summary>Section 1</summary>
        <p>Content 1</p>
    </details>
    <details>
        <summary>Section 2</summary>
        <p>Content 2</p>
    </details>
    """
    )

    # Should be able to find specific summary by name
    section1 = get_by_role(container, "button", name="Section 1")
    assert section1 is not None
    assert section1.tag == "summary"
    assert get_text_content(section1) == "Section 1"

    section2 = get_by_role(container, "button", name="Section 2")
    assert section2 is not None
    assert section2.tag == "summary"
    assert get_text_content(section2) == "Section 2"


def test_get_all_buttons_includes_summary():
    """Test that get_all_by_role finds both <button> and <summary> elements."""
    container = html(
        t"""
    <div>
        <button>Regular button</button>
        <details>
            <summary>Expandable section</summary>
            <p>Content</p>
        </details>
        <button>Another button</button>
    </div>
    """
    )

    # Should find all button-like elements including summary
    buttons = get_all_by_role(container, "button")
    assert len(buttons) == 3

    # Verify the types
    assert buttons[0].tag == "button"
    assert buttons[1].tag == "summary"
    assert buttons[2].tag == "button"


def test_get_role_for_summary_element():
    """Test that get_role_for_element returns 'button' for summary."""
    summary = html(t"""<summary>Test</summary>""")
    role = get_role_for_element(summary)
    assert role == "button"


# ===== Tag Name Query Tests =====


def test_query_by_tag_name_found():
    """Test query_by_tag_name finds first matching element."""
    container = html(t"""<div>
        <p>First</p>
        <span>Middle</span>
        <p>Last</p>
    </div>""")

    element = query_by_tag_name(container, "span")
    assert element is not None
    assert element.tag == "span"


def test_query_by_tag_name_not_found():
    """Test query_by_tag_name returns None when not found."""
    container = html(t"<div><p>Text</p></div>")

    element = query_by_tag_name(container, "span")
    assert element is None


def test_get_by_tag_name_success():
    """Test get_by_tag_name finds element."""
    container = html(t"<div><article>Content</article></div>")

    element = get_by_tag_name(container, "article")
    assert element.tag == "article"


def test_get_by_tag_name_not_found():
    """Test get_by_tag_name raises error when not found."""
    from aria_testing import ElementNotFoundError

    container = html(t"<div><p>Text</p></div>")

    with pytest.raises(ElementNotFoundError) as exc_info:
        get_by_tag_name(container, "article")
    assert "Unable to find element with tag 'article'" in str(exc_info.value)


def test_get_by_tag_name_multiple_elements():
    """Test get_by_tag_name raises error with multiple matches."""
    from aria_testing import MultipleElementsError

    container = html(t"""<div>
        <p>First</p>
        <p>Second</p>
    </div>""")

    with pytest.raises(MultipleElementsError):
        get_by_tag_name(container, "p")


def test_query_all_by_tag_name():
    """Test query_all_by_tag_name finds all matching elements."""
    container = html(t"""<div>
        <p>First</p>
        <span>Middle</span>
        <p>Second</p>
        <p>Third</p>
    </div>""")

    elements = query_all_by_tag_name(container, "p")
    assert len(elements) == 3
    assert all(el.tag == "p" for el in elements)


def test_get_all_by_tag_name_success():
    """Test get_all_by_tag_name finds all elements."""
    container = html(t"""<div>
        <li>Item 1</li>
        <li>Item 2</li>
    </div>""")

    elements = get_all_by_tag_name(container, "li")
    assert len(elements) == 2


def test_get_all_by_tag_name_not_found():
    """Test get_all_by_tag_name raises error when none found."""
    from aria_testing import ElementNotFoundError

    container = html(t"<div><p>Text</p></div>")

    with pytest.raises(ElementNotFoundError):
        get_all_by_tag_name(container, "article")


def test_tag_name_with_attrs_filter():
    """Test tag name queries with attribute filtering."""
    container = html(t"""<div>
        <link rel="stylesheet" href="style.css" />
        <link rel="icon" href="favicon.ico" />
        <link rel="stylesheet" href="other.css" />
    </div>""")

    # Find all stylesheets
    stylesheets = query_all_by_tag_name(container, "link", attrs={"rel": "stylesheet"})
    assert len(stylesheets) == 2
    for link in stylesheets:
        assert link.attrs.get("rel") == "stylesheet"

    # Find the icon
    icon = query_by_tag_name(container, "link", attrs={"rel": "icon"})
    assert icon is not None
    assert icon.attrs.get("href") == "favicon.ico"


def test_tag_name_with_multiple_attrs():
    """Test tag name queries with multiple attribute filters."""
    container = html(t"""<div>
        <input type="text" name="username" />
        <input type="password" name="password" />
        <input type="text" name="email" />
    </div>""")

    # Find text input with specific name
    element = get_by_tag_name(
        container, "input", attrs={"type": "text", "name": "email"}
    )
    assert element.attrs.get("type") == "text"
    assert element.attrs.get("name") == "email"


def test_tag_name_case_insensitive():
    """Test that tag name matching is case-insensitive."""
    container = html(t"<div><P>Text</P></div>")

    # Should find it regardless of case
    element = query_by_tag_name(container, "p")
    assert element is not None
    assert element.tag.lower() == "p"


def test_tag_name_attrs_no_match():
    """Test tag name query with attrs that don't match."""
    container = html(t"""<div>
        <link rel="stylesheet" href="style.css" />
    </div>""")

    # Should not find icon
    icon = query_by_tag_name(container, "link", attrs={"rel": "icon"})
    assert icon is None

    # Should raise error with get_by
    from aria_testing import ElementNotFoundError

    with pytest.raises(ElementNotFoundError):
        get_by_tag_name(container, "link", attrs={"rel": "icon"})


def test_tag_name_with_in_class():
    """Test tag name queries with in_class special attribute."""
    container = html(
        t"""<div>
        <header class="is-fixed header-main">Main Header</header>
        <header class="header-secondary">Secondary Header</header>
        <div class="is-fixed sidebar">Sidebar</div>
    </div>"""
    )

    # Find the header with 'is-fixed' in class
    fixed_header = get_by_tag_name(container, "header", attrs={"in_class": "is-fixed"})
    assert fixed_header is not None
    _class = fixed_header.attrs.get("class", "")
    assert _class is not None
    assert "is-fixed" in _class

    # Find all elements with 'is-fixed' (should only find divs when searching divs)
    fixed_divs = query_all_by_tag_name(container, "div", attrs={"in_class": "is-fixed"})
    # Note: The outer div doesn't have is-fixed, only the inner one
    assert len(fixed_divs) == 1
    _class = fixed_divs[0].attrs.get("class", "")
    assert _class is not None
    assert "sidebar" in _class


def test_tag_name_in_class_substring_match():
    """Test that in_class does substring matching on class attribute."""
    container = html(
        t"""<div>
        <button class="btn btn-primary">Primary</button>
        <button class="btn btn-secondary">Secondary</button>
        <button class="link-button">Link Button</button>
    </div>"""
    )

    # Find buttons with 'btn-primary' in class
    primary_btns = query_all_by_tag_name(
        container, "button", attrs={"in_class": "btn-primary"}
    )
    assert len(primary_btns) == 1
    assert "Primary" in str(primary_btns[0].children[0])

    # Find buttons with just 'btn' in class (should match first two)
    btn_buttons = query_all_by_tag_name(container, "button", attrs={"in_class": "btn"})
    assert len(btn_buttons) == 2


def test_tag_name_in_class_combined_with_attrs():
    """Test combining in_class with regular attribute matching."""
    container = html(
        t"""<div>
        <a href="/home" class="nav-link active">Nav Home</a>
        <a href="/about" class="nav-link">About</a>
        <a href="/home" class="footer-link">Footer Home</a>
    </div>"""
    )

    # Find link with specific href AND nav-link class
    nav_home = get_by_tag_name(
        container, "a", attrs={"href": "/home", "in_class": "nav-link"}
    )
    assert nav_home is not None
    assert nav_home.attrs.get("href") == "/home"
    _class = nav_home.attrs.get("class", "")
    assert _class is not None
    assert "nav-link" in _class

    # Should not find footer link when looking for nav-link
    result = query_by_tag_name(
        container, "a", attrs={"href": "/about", "in_class": "footer-link"}
    )
    assert result is None


def test_tag_name_in_class_no_match():
    """Test in_class when class doesn't match."""
    container = html(
        t"""<div>
        <button class="btn-primary">Button</button>
    </div>"""
    )

    # Should not find button with non-existent class
    result = query_by_tag_name(container, "button", attrs={"in_class": "btn-secondary"})
    assert result is None


def test_tag_name_in_class_empty_class():
    """Test in_class when element has no class attribute."""
    container = html(
        t"""<div>
        <button>No Class</button>
    </div>"""
    )

    # Should not match elements without class
    result = query_by_tag_name(container, "button", attrs={"in_class": "any-class"})
    assert result is None


def test_tag_name_in_class_multiple_classes():
    """Test in_class with elements having multiple classes."""
    container = html(
        t"""<div>
        <div class="container flex-row justify-center">Content</div>
    </div>"""
    )

    # Should match any substring in the class attribute
    result = query_by_tag_name(container, "div", attrs={"in_class": "flex-row"})
    assert result is not None

    result = query_by_tag_name(container, "div", attrs={"in_class": "justify-center"})
    assert result is not None

    result = query_by_tag_name(container, "div", attrs={"in_class": "container"})
    assert result is not None


# ===== Class Name Query Tests =====


def test_query_by_class_finds_element_with_multiple_classes():
    container = html(t"""<div>
        <h1 class="title hero">Welcome</h1>
        <p class="message lead">Hello</p>
    </div>""")

    el = get_by_class(container, "message")
    assert el is not None
    assert el.tag == "p"
    _class = el.attrs.get("class", "")
    assert _class is not None
    assert "message" in _class


def test_query_by_class_not_found_returns_none():
    container = html(t"""<div>
        <p class="a b">A</p>
    </div>""")

    assert query_by_class(container, "missing") is None


def test_get_by_class_success():
    container = html(t"""<div>
        <button class="btn primary">Save</button>
    </div>""")

    el = get_by_class(container, "btn")
    assert el.tag == "button"


def test_get_by_class_duplicate_raises_multiple():
    container = html(t"""<div>
        <span class="dup">X</span>
        <span class="dup">Y</span>
    </div>""")

    with pytest.raises(MultipleElementsError) as exc:
        get_by_class(container, "dup")
    assert isinstance(exc.value, MultipleElementsError)


def test_class_token_matching_is_not_substring():
    container = html(t"""<div>
        <div class="button other"></div>
        <div class="btn other"></div>
    </div>""")

    # Should not match substring 'btn' within 'button'
    assert get_by_class(container, "btn").attrs.get("class") == "btn other"
    assert get_by_class(container, "button").attrs.get("class") == "button other"


def test_query_by_class_raises_on_multiple_matches():
    container = html(t"""<div>
        <div class="dup"></div>
        <span class="dup"></span>
    </div>""")

    with pytest.raises(MultipleElementsError):
        query_by_class(container, "dup")


def test_get_all_by_class_success_and_order():
    container = html(t"""<div>
        <p class="a x">1</p>
        <div class="b a">2</div>
        <span class="a">3</span>
    </div>""")

    elements = get_all_by_class(container, "a")
    assert [el.tag for el in elements] == ["p", "div", "span"]


def test_get_all_by_class_not_found_raises():
    container = html(t"""<div>
        <p class="x">1</p>
    </div>""")

    with pytest.raises(Exception) as exc:
        get_all_by_class(container, "missing")
    # Being explicit about the type keeps intent clear
    assert exc.type.__name__ == "ElementNotFoundError"


def test_query_all_by_class_returns_empty_or_list():
    container = html(t"""<div>
        <p class="m n">1</p>
        <div class="n">2</div>
    </div>""")

    assert query_all_by_class(container, "missing") == []
    elements = query_all_by_class(container, "n")
    assert len(elements) == 2
    assert {el.tag for el in elements} == {"p", "div"}


# ===== ID Query Tests =====


def test_query_by_id_finds_element():
    container = html(t"""<div>
        <h1 id="title">Welcome</h1>
        <p id="message">Hello</p>
    </div>""")

    el = query_by_id(container, "message")
    assert el is not None
    assert el.tag == "p"
    assert el.attrs.get("id") == "message"


def test_query_by_id_not_found_returns_none():
    container = html(t"""<div>
        <p id="a">A</p>
    </div>""")

    assert query_by_id(container, "missing") is None


def test_get_by_id_success():
    container = html(t"""<div>
        <button id="save">Save</button>
    </div>""")

    el = get_by_id(container, "save")
    assert el.tag == "button"


def test_get_by_id_not_found_raises():
    container = html(t"""<div>
        <p id="a">A</p>
    </div>""")

    with pytest.raises(ElementNotFoundError):
        get_by_id(container, "nope")


def test_get_by_id_duplicate_ids_raise_multiple():
    container = html(t"""<div>
        <span id="dup">X</span>
        <span id="dup">Y</span>
    </div>""")

    with pytest.raises(MultipleElementsError) as exc:
        get_by_id(container, "dup")
    assert isinstance(exc.value, MultipleElementsError)


# ===== Implicit Role Tests =====


def test_implicit_role_landmark_roles():
    """Test landmark role type hints work."""
    simple_document = html(t"""<div>
        <nav>Navigation</nav>
        <main>Main content</main>
        <button>Click me</button>
        <h1>Title</h1>
    </div>""")

    nav = get_by_role(simple_document, "navigation")
    assert nav.tag == "nav"

    main = get_by_role(simple_document, "main")
    assert main.tag == "main"


def test_implicit_role_widget_roles():
    """Test widget role type hints work."""
    simple_document = html(t"""<div>
        <nav>Navigation</nav>
        <main>Main content</main>
        <button>Click me</button>
        <h1>Title</h1>
    </div>""")

    button = get_by_role(simple_document, "button")
    assert button.tag == "button"


def test_implicit_role_document_structure_roles():
    """Test document structure role type hints work."""
    simple_document = html(t"""<div>
        <nav>Navigation</nav>
        <main>Main content</main>
        <button>Click me</button>
        <h1>Title</h1>
    </div>""")

    heading = get_by_role(simple_document, "heading")
    assert heading.tag == "h1"


def test_implicit_role_type_checking_example():
    """Demonstrate type checking works for role parameters."""
    doc = html(t"<div><nav>Navigation</nav></div>")

    # These should all work with proper type hints
    nav1 = get_by_role(doc, "navigation")  # Literal string

    # Type annotations should prevent invalid roles at type-check time
    assert nav1.tag == "nav"


# ===== Label Text Query Tests =====


def test_query_by_label_text_aria_label():
    """Test finding element by aria-label attribute."""
    document = html(t"""
        <div>
            <input type="text" aria-label="Enter your name" />
            <button aria-label="Submit form">Submit</button>
        </div>
    """)

    input_element = query_by_label_text(document, "Enter your name")
    assert input_element is not None
    assert input_element.tag == "input"
    assert input_element.attrs.get("type") == "text"

    button_element = query_by_label_text(document, "Submit form")
    assert button_element is not None
    assert button_element.tag == "button"


def test_query_by_label_text_not_found():
    """Test query_by_label_text returns None when not found."""
    document = html(t'<div><input type="text" /></div>')

    element = query_by_label_text(document, "Not found")
    assert element is None


def test_get_by_label_text_success():
    """Test get_by_label_text finds element successfully."""
    document = html(t'<div><input aria-label="Search" type="text" /></div>')

    element = get_by_label_text(document, "Search")
    assert element.tag == "input"
    assert element.attrs.get("aria-label") == "Search"


def test_get_by_label_text_not_found():
    """Test get_by_label_text raises error when not found."""
    document = html(t'<div><input type="text" /></div>')

    with pytest.raises(ElementNotFoundError) as exc_info:
        get_by_label_text(document, "Not found")
    assert "Unable to find element with label text: Not found" in str(exc_info.value)


def test_get_by_label_text_multiple_elements():
    """Test get_by_label_text raises error when multiple elements found."""
    document = html(t"""
        <div>
            <input aria-label="Name" type="text" />
            <input aria-label="Full Name" type="text" />
        </div>
    """)

    with pytest.raises(MultipleElementsError) as exc_info:
        get_by_label_text(document, "Name")
    assert "Found multiple elements with label text: Name" in str(exc_info.value)
    assert isinstance(exc_info.value, MultipleElementsError)
    assert exc_info.value.count == 2


def test_query_all_by_label_text():
    """Test query_all_by_label_text finds multiple elements."""
    document = html(t"""
        <div>
            <input aria-label="User Name" type="text" />
            <input aria-label="Display Name" type="text" />
            <textarea aria-label="Name Description"></textarea>
        </div>
    """)

    elements = query_all_by_label_text(document, "Name")
    assert len(elements) == 3
    assert elements[0].tag == "input"
    assert elements[1].tag == "input"
    assert elements[2].tag == "textarea"


def test_get_all_by_label_text_success():
    """Test get_all_by_label_text finds multiple elements."""
    document = html(t"""
        <div>
            <button aria-label="Save Document">Save</button>
            <button aria-label="Save As">Save As</button>
        </div>
    """)

    elements = get_all_by_label_text(document, "Save")
    assert len(elements) == 2
    assert all(el.tag == "button" for el in elements)


def test_get_all_by_label_text_not_found():
    """Test get_all_by_label_text raises error when no elements found."""
    document = html(t'<div><input type="text" /></div>')

    with pytest.raises(ElementNotFoundError):
        get_all_by_label_text(document, "Not found")


def test_label_with_for_attribute():
    """Test finding element by label with 'for' attribute."""
    document = html(t"""
        <div>
            <label for="username">Username</label>
            <input id="username" type="text" />
        </div>
    """)

    element = get_by_label_text(document, "Username")
    assert element.tag == "input"
    assert element.attrs.get("id") == "username"
    assert element.attrs.get("type") == "text"


def test_nested_label():
    """Test finding element nested inside label."""
    document = html(t"""
        <div>
            <label>
                Email Address
                <input type="email" />
            </label>
        </div>
    """)

    element = get_by_label_text(document, "Email Address")
    assert element.tag == "input"
    assert element.attrs.get("type") == "email"


def test_nested_label_with_multiple_controls():
    """Test finding elements nested inside label with multiple controls."""
    document = html(t"""
        <div>
            <label>
                Contact Information
                <input type="text" placeholder="Name" />
                <input type="email" placeholder="Email" />
                <textarea placeholder="Message"></textarea>
            </label>
        </div>
    """)

    elements = get_all_by_label_text(document, "Contact Information")
    assert len(elements) == 3
    assert elements[0].tag == "input" and elements[0].attrs.get("type") == "text"
    assert elements[1].tag == "input" and elements[1].attrs.get("type") == "email"
    assert elements[2].tag == "textarea"


def test_aria_labelledby():
    """Test finding element by aria-labelledby reference."""
    document = html(t"""
        <div>
            <div id="name-label">Full Name</div>
            <input type="text" aria-labelledby="name-label" />
        </div>
    """)

    element = get_by_label_text(document, "Full Name")
    assert element.tag == "input"
    assert element.attrs.get("aria-labelledby") == "name-label"


def test_aria_labelledby_multiple_references():
    """Test finding element by aria-labelledby with multiple IDs."""
    document = html(t"""
        <div>
            <div id="first-label">First</div>
            <div id="last-label">Last Name</div>
            <input type="text" aria-labelledby="first-label last-label" />
        </div>
    """)

    # Should find by either label
    element1 = get_by_label_text(document, "First")
    assert element1.tag == "input"

    element2 = get_by_label_text(document, "Last Name")
    assert element2.tag == "input"

    # Same element should be found
    assert element1 is element2


def test_multiple_labeling_methods():
    """Test element with multiple labeling methods (should not duplicate)."""
    document = html(t"""
        <div>
            <label for="multi-input">Multi Label</label>
            <input id="multi-input" type="text" aria-label="Multi Label Input" />
        </div>
    """)

    # Both "Multi Label" and "Multi Label Input" should find the same element
    element1 = get_by_label_text(document, "Multi Label")
    element2 = get_by_label_text(document, "Multi Label Input")

    assert element1.tag == "input"
    assert element2.tag == "input"
    # They should be the same element for "Multi Label" case
    # But different matches for different label texts


def test_partial_text_matching_label():
    """Test that label text matching works with partial text."""
    document = html(t"""
        <div>
            <input aria-label="Enter your email address" type="email" />
            <button aria-label="Submit the form">Submit</button>
        </div>
    """)

    # Should find by partial match
    email_input = get_by_label_text(document, "email")
    assert email_input.tag == "input"
    assert email_input.attrs.get("type") == "email"

    submit_button = get_by_label_text(document, "Submit")
    assert submit_button.tag == "button"


def test_case_sensitive_matching_label():
    """Test that label text matching is case sensitive."""
    document = html(t'<div><input aria-label="Username" type="text" /></div>')

    # Should find exact case
    element = get_by_label_text(document, "Username")
    assert element is not None

    # Should not find different case
    element = query_by_label_text(document, "username")
    assert element is None

    element = query_by_label_text(document, "USERNAME")
    assert element is None


def test_complex_form():
    """Test finding elements in a complex form with mixed labeling approaches."""
    document = html(t"""
        <form>
            <div>
                <label for="name">Name</label>
                <input id="name" type="text" />
            </div>

            <div>
                <label>
                    Email
                    <input type="email" />
                </label>
            </div>

            <div>
                <div id="phone-label">Phone Number</div>
                <input type="tel" aria-labelledby="phone-label" />
            </div>

            <div>
                <input type="password" aria-label="Password" />
            </div>

            <button type="submit" aria-label="Submit Form">Submit</button>
        </form>
    """)

    # Test each labeling method
    name_input = get_by_label_text(document, "Name")
    assert name_input.attrs.get("id") == "name"

    email_input = get_by_label_text(document, "Email")
    assert email_input.attrs.get("type") == "email"

    phone_input = get_by_label_text(document, "Phone Number")
    assert phone_input.attrs.get("type") == "tel"

    password_input = get_by_label_text(document, "Password")
    assert password_input.attrs.get("type") == "password"

    submit_button = get_by_label_text(document, "Submit Form")
    assert submit_button.tag == "button"
    assert submit_button.attrs.get("type") == "submit"


def test_label_without_associated_control():
    """Test that labels without associated controls are ignored."""
    document = html(t"""
        <div>
            <label>Standalone Label</label>
            <div>Some content</div>
        </div>
    """)

    # Should not find anything since label isn't associated with a form control
    element = query_by_label_text(document, "Standalone Label")
    assert element is None


def test_non_form_elements_with_aria_label():
    """Test that non-form elements with aria-label are found."""
    document = html(t"""
        <div>
            <div aria-label="Important Notice">This is important</div>
            <span aria-label="Help Text">?</span>
            <article aria-label="Main Article">Article content</article>
        </div>
    """)

    notice = get_by_label_text(document, "Important Notice")
    assert notice.tag == "div"

    help_text = get_by_label_text(document, "Help Text")
    assert help_text.tag == "span"

    article = get_by_label_text(document, "Main Article")
    assert article.tag == "article"


def test_fragment_as_container_label():
    """Test using fragment as container."""
    fragment = html(t"""
        <input aria-label="First Field" type="text" />
        <input aria-label="Second Field" type="text" />
    """)

    first_field = get_by_label_text(fragment, "First Field")
    assert first_field.tag == "input"

    elements = get_all_by_label_text(fragment, "Field")
    assert len(elements) == 2
