import urllib2
import httplib


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
        except (httplib.BadStatusLine, IOError):
            return None, 404