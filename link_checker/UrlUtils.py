import urlparse


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
        return parts[0] and parts[1]

    @staticmethod
    def normalize(base_uri, uri):
        if UrlUtils.is_relative(uri):
            return UrlUtils.to_absolute(base_uri, uri)
        return uri