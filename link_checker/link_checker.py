import sys
import urlparse
import urllib

from HTMLParser import HTMLParser
from threading import Thread


class Link(object):
    def __init__(self, href):
        self.href = href
        self.exists = False
        self.checked = False


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
        self.collected_links = self._checker.check_for_worker(self._link)


class HttpProvider(object):
    @staticmethod
    def fetch(uri):
        try:
            print("Processing: {0}".format(uri))
            source = urllib.urlopen(uri)
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
        return UrlWorker.to_absolute(base_uri, uri1) == UrlWorker.to_absolute(base_uri, uri2)

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
    max_threads = 10

    def __init__(self, base_uri, http_provider):
        error = r"The uri format is protocol://domain.com"
        if not UrlWorker.has_schema(base_uri):
            raise ValueError(error)
        self._base_uri = base_uri
        self._http_provider = http_provider
        self._links = [Link(base_uri)]
        self._index = 0

    def check(self):
        while self.has_unchecked_links(self._links):
            unchecked_links = [link for link in self._links if link.checked is False]
            workers = []
            for link in unchecked_links[0:self.max_threads]:
                worker = Worker(link, self)
                workers.append(worker)

            for worker in workers:
                worker.daemon = True
                worker.start()

            for worker in workers:
                worker.join()

            for worker in workers:
                collected_links = worker.collected_links
                if len(collected_links) > 0:
                    unique = [Link(l) for l in filter(self._is_new, collected_links)]
                    self._links.extend(unique)

        ConsoleReporter.report(self._links)

    def _check(self, link):
        if UrlWorker.is_internal(self._base_uri, link.href):
            if UrlWorker.is_relative(link.href):
                link.href = UrlWorker.to_absolute(self._base_uri, link.href)
            html, code = self._http_provider.fetch(link.href)
            if code == 200 and html:
                link.exists = True
                self._links.extend([Link(l) for l in filter(self._is_new, set(UrlLister().parse(html)))])
        else:
            html, code = self._http_provider.fetch(link.href)
            link.exists = bool(code == 200 and html)

    def check_for_worker(self, link):
        links = []
        if UrlWorker.is_internal(self._base_uri, link.href):
            if UrlWorker.is_relative(link.href):
                link.href = UrlWorker.to_absolute(self._base_uri, link.href)
            html, code = self._http_provider.fetch(link.href)
            if code == 200 and html:
                link.exists = True
                link.checked = True
                links = list(set(UrlLister().parse(html)))
        else:
            html, code = self._http_provider.fetch(link.href)
            link.exists = bool(code == 200 and html)
            link.checked = True
        return links

    def _is_new(self, href):
        for link in self._links:
            if UrlWorker.is_equal(self._base_uri, link.href, href):
                return False
        return True

    def has_unchecked_links(self, _links):
        unchecked_links = [link for link in _links if link.checked is False]
        return len(unchecked_links) > 0


class ConsoleReporter(object):
    @staticmethod
    def report(links):
        out = "Total links checked: {0}.\n".format(len(links))
        broken_links = [link for link in links if link.checked and not link.exists]
        if len(broken_links) > 0:
            out += "Broken links: {0}.\n".format(len(broken_links))
            for link in broken_links:
                out += link.href
                out += "\n"
        print(out)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        site = sys.argv[1]
        link_checker = LinkChecker(site, HttpProvider)
        link_checker.check()
    else:
        raise ValueError("Please pass one argument which is website URL in the format of protocol://domain")
