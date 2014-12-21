from link_checker.UrlUtils import UrlUtils

base_uri = "http://foo.com"


def test_for_internal_links():
    assert UrlUtils.is_internal(base_uri, "www.foo.com/item") is True
    assert UrlUtils.is_internal(base_uri, "http://foo.com/item") is True
    assert UrlUtils.is_internal(base_uri, "foo.com") is True
    assert UrlUtils.is_internal(base_uri, "/foo.php") is True
    assert UrlUtils.is_internal(base_uri, "\foo.php") is True
    assert UrlUtils.is_internal(base_uri, "www.bar.com") is True
    assert UrlUtils.is_internal(base_uri, "bar.com") is True
    assert UrlUtils.is_internal(base_uri, "/") is True
    assert UrlUtils.is_internal(base_uri, "\\") is True


def test_for_external_links():
    assert UrlUtils.is_internal(base_uri, "http://bar.com/item") is False
    assert UrlUtils.is_internal(base_uri, "https://foo.com/item") is False


def test_for_relative_links():
    assert UrlUtils.is_relative("/foo.php") is True
    assert UrlUtils.is_relative("\foo.php") is True
    assert UrlUtils.is_relative("\\") is True
    assert UrlUtils.is_relative("/") is True
    assert UrlUtils.is_relative("www.foo.com/item") is True
    assert UrlUtils.is_relative("foo.com/item") is True
    assert UrlUtils.is_relative("foo.com/item") is True


def test_for_absolute_links():
    assert UrlUtils.is_relative("http://foo.com/item") is False
    assert UrlUtils.is_relative("https://foo.com/item") is False
    assert UrlUtils.is_relative("ftp://foo.com/item") is False


def test_to_absolute():
    assert UrlUtils.to_absolute(base_uri, "/") == "http://foo.com/"
    assert UrlUtils.to_absolute("http://foo.com/", "/") == "http://foo.com/"
    assert UrlUtils.to_absolute("http://foo.com", "/item") == "http://foo.com/item"
    assert UrlUtils.to_absolute("http://foo.com/", "/item") == "http://foo.com/item"
    assert UrlUtils.to_absolute("http://foo.com/", "item") == "http://foo.com/item"
    assert UrlUtils.to_absolute("http://foo.com", "item") == "http://foo.com/item"


def test_normalize():
    assert UrlUtils.normalize("https://foo.com/", "//foo.com/awesome.php") == "https://foo.com/awesome.php"
    assert UrlUtils.normalize("http://foo.com", "/awesome.php") == "http://foo.com/awesome.php"


def test_has_schema():
    assert UrlUtils.has_schema("https://google.com") is True
    assert UrlUtils.has_schema("www.awesome.com") is False