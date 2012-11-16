from lxml.html import fromstring


class Finder(object):

    def __init__(self):
        super(Finder, self).__init__()
        self.searchers = [XPathSearch, CSSSearch, LinkSearch, AnchorTextSearch]

    def search(self, pagetext, config):
        page = fromstring(pagetext)
        nodes = []

        for searcher in self.searchers:
            config_key = searcher.__name__.lower().replace('search', '')
            option = config.get(config_key, {})
            if option:
                nodes = searcher().process(page, nodes, option)

        return nodes


class XPathSearch(object):

    def process(self, page, nodelist, config):
        """
        Search the page using the config xpath instruction to
        locate links and add them to the nodelist
        """
        nodelist.append('Errk')
        return nodelist


class CSSSearch(object):

    def process(self, page, nodelist, config):
        """
        Search the page using the config css selector to
        locate links and add them to the nodelist
        """
        nodes = page.cssselect(config)
        nodelist.extend(nodes)
        return nodelist


class LinkSearch(object):

    def process(self, page, nodelist, config):
        """
        Apply the regex in config to all node hrefs in the nodelist
        """
        nodelist.append('LinkS')
        return nodelist


class AnchorTextSearch(object):

    def process(self, page, nodelist, config):
        """
        Apply the regex in config to all node text in the nodelist
        """
        nodelist.append('Anchor')
        return nodelist
