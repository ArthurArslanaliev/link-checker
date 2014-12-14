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