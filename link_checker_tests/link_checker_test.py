from link_checker.LinkChecker import LinkChecker

test_link = r"<a href='https://bar.com'><\a>"
test_uri = r"http://foo.com"


class TestHtmlParser(object):
    def __init__(self):
        self.links = []

    def parse(self, html):
        self.links.append(test_link)
        self.links.append(test_link)
        return self.links


class TestHttpProvider(object):
    @staticmethod
    def fetch(uri):
        return "<html>%s</html>" % uri, 200


checker = LinkChecker(test_uri, TestHtmlParser(), TestHttpProvider())


def test_check():
    checker.check()
    assert len(checker._links) == 2
