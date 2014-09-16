from link_checker.link_checker import UrlWorker

base_uri = "http://foo.com"


def test_for_internal_links():
    assert UrlWorker.is_internal(base_uri, "www.foo.com/item") is True
    assert UrlWorker.is_internal(base_uri, "http://foo.com/item") is True
    assert UrlWorker.is_internal(base_uri, "foo.com") is True
    assert UrlWorker.is_internal(base_uri, "/foo.php") is True
    assert UrlWorker.is_internal(base_uri, "\foo.php") is True
    assert UrlWorker.is_internal(base_uri, "www.bar.com") is True
    assert UrlWorker.is_internal(base_uri, "bar.com") is True
    assert UrlWorker.is_internal(base_uri, "/") is True
    assert UrlWorker.is_internal(base_uri, "\\") is True


def test_for_external_links():
    assert UrlWorker.is_internal(base_uri, "http://bar.com/item") is False
    assert UrlWorker.is_internal(base_uri, "https://foo.com/item") is False


def test_for_relative_links():
    assert UrlWorker.is_relative("/foo.php") is True
    assert UrlWorker.is_relative("\foo.php") is True
    assert UrlWorker.is_relative("\\") is True
    assert UrlWorker.is_relative("/") is True
    assert UrlWorker.is_relative("www.foo.com/item") is True
    assert UrlWorker.is_relative("foo.com/item") is True
    assert UrlWorker.is_relative("foo.com/item") is True


def test_for_absolute_links():
    assert UrlWorker.is_relative("http://foo.com/item") is False
    assert UrlWorker.is_relative("https://foo.com/item") is False
    assert UrlWorker.is_relative("ftp://foo.com/item") is False


def test_to_absolute():
    assert UrlWorker.to_absolute(base_uri, "/") == "http://foo.com/"
    assert UrlWorker.to_absolute("http://foo.com/", "/") == "http://foo.com/"
    assert UrlWorker.to_absolute("http://foo.com", "/item") == "http://foo.com/item"
    assert UrlWorker.to_absolute("http://foo.com/", "/item") == "http://foo.com/item"
    assert UrlWorker.to_absolute("http://foo.com/", "item") == "http://foo.com/item"
    assert UrlWorker.to_absolute("http://foo.com", "item") == "http://foo.com/item"