import os
from link_checker.UrlLister import UrlLister
from link_checker.LinkChecker import Link

test_data = "test_data"


def test_link_init():
    link = Link("foo-bar")
    assert link.exists is False


def test_init():
    assert len(UrlLister().links) == 0


def test_parsing():
    test_parser = "valid_html.html"
    path = os.path.join(os.path.dirname(__file__), test_data, test_parser)
    with open(path) as f:
        html = f.read()
        parser = UrlLister()
        parser.parse(html)
        assert len(parser.links) == 3


def test_empty_link():
    html = r"<a><\a>"
    parser = UrlLister()
    parser.parse(html)
    assert len(parser.links) == 0