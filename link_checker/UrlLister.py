from HTMLParser import HTMLParser


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