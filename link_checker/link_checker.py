import urllib
import urlparse
from sgmllib import SGMLParser


class Link(object):
    def __init__(self, href):
        self.href = href
        self.exists = False


class HtmlParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.links = []

    def start_a(self, attr):
        href = [v for k, v in attr if k == "href"]
        if len(href) == 1:
            self.links.append(href[0])

    def parse(self, html):
        self.feed(html)
        self.close()
        return self.links


class HttpProvider(object):
    @staticmethod
    def fetch(uri):
        try:
            print("Processing: {0}".format(uri))
            source = urllib.urlopen(uri)
            html = source.read()
            code = source.getcode()
            source.close()
            return html, code
        except IOError:
            return None, 404


class UrlWorker(object):
    @staticmethod
    def is_relative(uri):
        uri = UrlWorker.escape(uri)
        parts = urlparse.urlparse(uri)
        return not parts[1]

    @staticmethod
    def is_internal(base_uri, uri):
        uri = UrlWorker.escape(uri)
        if uri.startswith(base_uri):
            return True
        parts = urlparse.urlparse(uri)
        if not parts[0] and not parts[1]:
            return True
        return False

    @staticmethod
    def to_absolute(base_uri, uri):
        return urlparse.urljoin(base_uri, uri)

    @staticmethod
    def is_equal(base_uri, uri1, uri2):
        return UrlWorker.to_absolute(base_uri, uri1) == UrlWorker.to_absolute(base_uri, uri2)

    @staticmethod
    def escape(uri):
        return uri.encode("string-escape")

    @staticmethod
    def has_schema(uri):
        parts = urlparse.urlparse(uri)
        return parts[0] and parts[1]


class LinkChecker(object):
    def __init__(self, base_uri, html_parser, http_provider):
        error = r"The uri format is protocol://domain.com"
        if not UrlWorker.has_schema(base_uri):
            raise Exception(error)
        self._base_uri = base_uri
        self._html_parser = html_parser
        self._http_provider = http_provider
        self._links = [Link(base_uri)]
        self._index = 0

    def check(self):
        while self._index < len(self._links):
            self._check(self._links[self._index])
            self._index += 1

    def _check(self, link):
        if UrlWorker.is_internal(self._base_uri, link.href):
            if UrlWorker.is_relative(link.href):
                link.href = UrlWorker.to_absolute(self._base_uri, link.href)
            html, code = self._http_provider.fetch(link.href)
            if code == 200 and html:
                link.exists = True
                self._links.extend([Link(l) for l in filter(self._is_new, set(self._html_parser.parse(html)))])
        else:
            html, code = self._http_provider.fetch(link.href)
            link.exists = bool(code == 200 and html)

    def _is_new(self, uri):
        for link in self._links:
            if UrlWorker.is_equal(self._base_uri, link.href, uri):
                return False
        return True


if __name__ == "__main__":
    link_checker = LinkChecker("http://devcenter.spscommerce.com/", HtmlParser(), HttpProvider)
    link_checker.check()