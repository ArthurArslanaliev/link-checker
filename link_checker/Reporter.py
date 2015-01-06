import sys


class ConsoleReporter(object):
    @staticmethod
    def report(links):
        out = ['\rtotal links checked: {0}.\n'.format(len(links))]
        broken_links = [k for k, v in links.iteritems() if v['checked'] and not v['exists']]
        if len(broken_links) > 0:
            out.append('broken links: {0}.\n'.format(len(broken_links)))
            for link in broken_links:
                out.append(link)
                out.append('\n')

        sys.stdout.write(''.join(out))