import os
from link_checker.link_checker import Link, HtmlParser

test_data = "test_data"


def test_link_init():
    link = Link("foo-bar")
    assert link.exists is False


def test_init():
    assert len(HtmlParser().links) == 0


def test_parsing():
    test_parser = "valid_html.html"
    with open(os.path.join(os.getcwd(), test_data, test_parser)) as f:
        html = f.read()
        parser = HtmlParser()
        parser.parse(html)
        assert len(parser.links) == 3


def test_empty_link():
    html = r"<a><\a>"
    parser = HtmlParser()
    parser.parse(html)
    assert len(parser.links) == 0