"""
Tests for aria_testing label text query functions.
"""

import pytest
from tdom.processor import html

from aria_testing.errors import ElementNotFoundError, MultipleElementsError
from aria_testing.queries import (
    get_all_by_label_text,
    get_by_label_text,
    query_all_by_label_text,
    query_by_label_text,
)


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


def test_partial_text_matching():
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


def test_case_sensitive_matching():
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


def test_fragment_as_container():
    """Test using fragment as container."""
    fragment = html(t"""
        <input aria-label="First Field" type="text" />
        <input aria-label="Second Field" type="text" />
    """)

    first_field = get_by_label_text(fragment, "First Field")
    assert first_field.tag == "input"

    elements = get_all_by_label_text(fragment, "Field")
    assert len(elements) == 2
