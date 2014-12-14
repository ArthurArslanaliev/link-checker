from link_checker.HttpProvider import HttpProvider


def test_invalid_uri():
    href = "javascript:void()"
    html, code = HttpProvider.fetch(href)
    assert html is None
    assert code == 404


def test_non_existing_uri():
    href = "http://life.is.awesome.com/"
    html, code = HttpProvider.fetch(href)
    assert html is None
    assert code == 404