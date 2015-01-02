from link_checker.UrlLister import UrlLister
from link_checker.LinkChecker import Worker

base_uri = "https://foo.bar.com"


class HttpProviderMock(object):
    existing_external_link = "https://foo.barz.com/about.html"

    not_existing_external_link = "https://foo.com/about.html"

    internal_link = "/help.html"

    html = '''<!DOCTYPE html>
                <html>
                    <head lang="en">
                        <meta charset="UTF-8">
                        <title></title>
                    </head>
                    <body>
                        <a href="/help.html"></a>
                        <a href="https://foo.bar.com/"></a>
                        <a href="https://google.com"></a>
                    </body>
                </html>'''

    @staticmethod
    def fetch(uri):
        if not uri:
            raise Exception("expect the uri argument")

        if uri is HttpProviderMock.existing_external_link:
            return "<html></html>", 200

        if uri is HttpProviderMock.not_existing_external_link:
            return "<html></html>", 404

        return HttpProviderMock.html, 200


def test_existing_external_link():
    external_link = [HttpProviderMock.existing_external_link, {"checked": False, "exists": False}]

    worker = Worker(base_uri, external_link, HttpProviderMock, UrlLister)
    worker.run()

    links = worker.collected_links

    assert len(links) == 0
    assert external_link[1]["checked"] is True
    assert external_link[1]["exists"] is True


def test_not_existing_external_link():
    external_link = [HttpProviderMock.not_existing_external_link, {"exists": False, "checked": False}]

    worker = Worker(base_uri, external_link, HttpProviderMock, UrlLister)
    worker.run()

    links = worker.collected_links

    assert len(links) == 0
    assert external_link[1]["checked"] is True
    assert external_link[1]["exists"] is False


def test_internal_link():
    internal_link = [HttpProviderMock.internal_link, {"exists": False, "checked": False}]

    worker = Worker(base_uri, internal_link, HttpProviderMock, UrlLister())
    worker.run()

    links = worker.collected_links

    assert len(links) == 3

    assert "https://foo.bar.com/help.html" in links
    assert "https://foo.bar.com/" in links
    assert "https://google.com" in links
