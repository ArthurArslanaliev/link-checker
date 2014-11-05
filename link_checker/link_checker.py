import sys
import urlparse
import urllib2

from HTMLParser import HTMLParser
from threading import Thread


class UrlLister(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.links = []

    def handle_starttag(self, tag, attr):
        if tag == 'a':
            href = [v for k, v in attr if k == "href"]
            if len(href) == 1:
                self.links.append(href[0])

    def parse(self, html):
        self.reset()
        self.feed(html)
        self.close()
        return self.links


class Worker(Thread):
    def __init__(self, link_object, checker):
        super(Worker, self).__init__()
        self._link = link_object
        self._checker = checker
        self.collected_links = []

    def run(self):
        self.collected_links = self._checker._check(self._link)


class HttpProvider(object):
    user_agent = 'Super Browser'

    @staticmethod
    def fetch(uri):
        try:
            print(uri.encode('UTF-8'))
            req = urllib2.Request(uri.encode('UTF-8'), headers={'User-Agent': HttpProvider.user_agent})
            source = urllib2.urlopen(req, timeout=5)
            encoding = source.headers.getparam('charset')
            if encoding:
                html = source.read().decode(encoding, errors="ignore")
            else:
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
        return UrlWorker.to_absolute(base_uri, uri1).rstrip('/') == UrlWorker.to_absolute(base_uri, uri2).rstrip('/')

    @staticmethod
    def escape(uri):
        if isinstance(uri, unicode):
            return uri.encode("unicode-escape")
        return uri.encode("string-escape")

    @staticmethod
    def has_schema(uri):
        parts = urlparse.urlparse(uri)
        return parts[0] and parts[1]


class LinkChecker(object):
    max_threads = 60

    invalid_uri_error = r"The uri format is protocol://domain.com"

    def __init__(self, base_uri, http_provider):
        if not UrlWorker.has_schema(base_uri):
            raise ValueError(self.invalid_uri_error)
        self._base_uri = base_uri
        self._http_provider = http_provider
        self._links = {base_uri: {"checked": False, "exists": False}}

    def check(self):
        while self._has_unchecked_links():
            unchecked_links = self._get_unchecked_links()
            workers = []
            for link in unchecked_links[0:self.max_threads]:
                worker = Worker(link, self)
                workers.append(worker)
                worker.daemon = True
                worker.start()

            for worker in workers:
                worker.join()
                collected_links = worker.collected_links
                if len(collected_links) > 0:
                    unique = {l: {"checked": False, "exists": False} for l in collected_links if l not in self._links}
                    self._links = dict(self._links.items() + unique.items())

        ConsoleReporter.report(self._links)

    def _check(self, link):
        links = []
        if UrlWorker.is_internal(self._base_uri, link[0]):
            if UrlWorker.is_relative(link[0]):
                link[0] = UrlWorker.to_absolute(self._base_uri, link[0])
            html, code = self._http_provider.fetch(link[0])
            if code == 200 and html:
                link[1]["exists"] = True
                links = list(set(UrlLister().parse(html)))
        else:
            html, code = self._http_provider.fetch(link[0])
            link[1]["exists"] = bool(code == 200 and html)
        link[1]["checked"] = True
        return links

    def _has_unchecked_links(self):
        return len(self._get_unchecked_links()) > 0

    def _get_unchecked_links(self):
        return [[k, v] for k, v in self._links.iteritems() if not v["checked"]]


class ConsoleReporter(object):
    @staticmethod
    def report(links):
        out = "Total links checked: {0}.\n".format(len(links))
        broken_links = [k for k, v in links.iteritems() if v["checked"] and not v["exists"]]
        if len(broken_links) > 0:
            out += "Broken links: {0}.\n".format(len(broken_links))
            for link in broken_links:
                out += link
                out += "\n"
        print(out)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        site = sys.argv[1]
        link_checker = LinkChecker(site, HttpProvider)
        link_checker.check()
    else:
        raise ValueError("Please pass one argument which is website URL in the format of protocol://domain")