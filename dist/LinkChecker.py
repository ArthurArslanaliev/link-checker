import sys
import urllib2
import httplib
import urlparse

from threading import Thread
from HTMLParser import HTMLParser


class HttpProvider(object):
    user_agent = u'Mozilla/5.0 (Windows NT 5.1; rv:10.0.1) Gecko/20100101 Firefox/10.0.1'

    @staticmethod
    def fetch(uri):
        try:
            req = urllib2.Request(uri.encode('utf-8'), headers={'User-Agent': HttpProvider.user_agent})
            source = urllib2.urlopen(req, timeout=5)
            code = source.getcode()

            if 'HTML' not in source.info().typeheader.upper():
                return None, code

            encoding = source.headers.getparam('charset')
            if encoding:
                html = source.read().decode(encoding, errors='ignore')
            else:
                html = source.read().decode('utf-8', errors='ignore')
            source.close()
            return html, code
        except httplib.BadStatusLine:
            return None, 404
        except IOError:
            return None, 404


class UrlLister(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.links = []

    def handle_starttag(self, tag, attr):
        if tag == 'a':
            href = [v for k, v in attr if k == "href"]
            if len(href) == 1 and href[0]:
                self.links.append(href[0])

    def parse(self, html):
        self.reset()
        self.feed(html)
        self.close()
        return self.links


class UrlUtils(object):
    @staticmethod
    def is_relative(uri):
        uri = UrlUtils.escape(uri)
        parts = urlparse.urlparse(uri)
        return not parts[1]

    @staticmethod
    def is_internal(base_uri, uri):
        uri = UrlUtils.escape(uri)
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
    def escape(uri):
        if isinstance(uri, unicode):
            return uri.encode("unicode-escape")
        return uri.encode("string-escape")

    @staticmethod
    def has_schema(uri):
        parts = urlparse.urlparse(uri)
        return parts[0] != '' and parts[1] != ''

    @staticmethod
    def normalize(base_uri, uri):
        if uri.startswith('//'):
            scheme = urlparse.urlparse(base_uri)[0]
            return '{0}:{1}'.format(scheme, uri)
        if UrlUtils.is_relative(uri):
            return UrlUtils.to_absolute(base_uri, uri)
        return uri


class Worker(Thread):
    def __init__(self, base_url, link, http_provider, url_lister):
        super(Worker, self).__init__()
        self._http = http_provider
        self._lister = url_lister
        self._link = link
        self._base_url = base_url
        self.collected_links = []

    def run(self):
        self.collected_links = self._check(self._link)

    def _check(self, link):
        links = []
        html, code = self._http.fetch(link[0])
        if code == 200:
            link[1]["exists"] = True
            if UrlUtils.is_internal(self._base_url, link[0]) and html:
                links = [UrlUtils.normalize(self._base_url, l) for l in list(set(self._lister.parse(html)))]
        else:
            link[1]["exists"] = False
        link[1]["checked"] = True
        return links


class LinkChecker(object):
    max_threads = 60

    invalid_uri_error = r"The uri format is protocol://domain.com"

    def __init__(self, base_uri, http_provider):
        if not UrlUtils.has_schema(base_uri):
            raise ValueError(self.invalid_uri_error)
        self._base_uri = base_uri
        self._http_provider = http_provider
        self._links = {base_uri: {"checked": False, "exists": False}}

    def check(self):
        while True:
            unchecked_links = self._get_unchecked_links()
            if len(unchecked_links) is 0:
                break
            workers = []
            for link in unchecked_links[0:self.max_threads]:
                worker = Worker(self._base_uri, link, self._http_provider, UrlLister())
                workers.append(worker)
                worker.daemon = True
                worker.start()

            for worker in workers:
                worker.join()
                collected_links = worker.collected_links
                if len(collected_links) > 0:
                    unique = {l: {"checked": False, "exists": False} for l in collected_links if l not in self._links}
                    self._links = dict(self._links.items() + unique.items())
                    self._print()

        ConsoleReporter.report(self._links)

    def _get_unchecked_links(self):
        return [[k, v] for k, v in self._links.iteritems() if not v["checked"]]

    def _print(self):
        sys.stdout.write("\rlinks collected: %s" % len(self._links))
        sys.stdout.flush()


class ConsoleReporter(object):
    @staticmethod
    def report(links):
        out = "\rtotal links checked: {0}.\n".format(len(links))
        broken_links = [k for k, v in links.iteritems() if v["checked"] and not v["exists"]]
        if len(broken_links) > 0:
            out += "broken links: {0}.\n".format(len(broken_links))
            for link in broken_links:
                out += link
                out += "\n"
        sys.stdout.write(out)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        site = sys.argv[1]
        link_checker = LinkChecker(site, HttpProvider)
        link_checker.check()
    else:
        raise ValueError("Please pass one argument which is website URL in the format of protocol://domain")