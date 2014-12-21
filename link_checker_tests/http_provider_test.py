from link_checker.HttpProvider import HttpProvider


def test_valid_uri():
    href = 'https://google.com'
    html, code = HttpProvider.fetch(href)
    assert len(html) > 0
    assert code == 200


def test_valid_resource():
    href = 'http://www.w3.org/Addressing/URL/url-spec.txt'
    html, code = HttpProvider.fetch(href)
    assert html is None
    assert code == 200


def test_invalid_uri():
    href = "javascript:void()"
    html, code = HttpProvider.fetch(href)
    assert html is None
    assert code == 404