from HTMLParser import HTMLParser


class UrlLister(HTMLParser):
    def reset(self):
        HTMLParser.reset(self)
        self.links = []

    def handle_starttag(self, tag, attr):
        if tag == 'a' or tag == 'link':
            self._save_to_links(attr, 'href')

        if tag == 'script':
            self._save_to_links(attr, 'src')

    def parse(self, html):
        self.reset()
        self.feed(html)
        self.close()
        return self.links

    def _save_to_links(self, attributes, attr_name):
        attr = [v for k, v in attributes if k == attr_name]
        if len(attr) == 1 and attr[0]:
            self.links.append(attr[0])
