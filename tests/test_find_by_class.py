import pytest
from tdom.processor import html

from aria_testing.errors import MultipleElementsError
from aria_testing.queries import (
    get_by_class,
    query_by_class,
    get_all_by_class,
    query_all_by_class,
)


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
