import pytest
from tdom.processor import html

from aria_testing.errors import ElementNotFoundError, MultipleElementsError
from aria_testing.queries import get_by_id, query_by_id


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
