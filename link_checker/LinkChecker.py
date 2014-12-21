import sys

from threading import Thread

from UrlLister import UrlLister
from HttpProvider import HttpProvider
from UrlUtils import UrlUtils
from Reporter import ConsoleReporter

# TODO: Update unit tests


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


if __name__ == "__main__":
    if len(sys.argv) == 2:
        site = sys.argv[1]
        link_checker = LinkChecker(site, HttpProvider)
        link_checker.check()
    else:
        raise ValueError("Please pass one argument which is website URL in the format of protocol://domain")