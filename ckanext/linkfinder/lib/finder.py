import re
import requests
from urlparse import urljoin
from lxml.html import fromstring

class Finder(object):

    def __init__(self, url):
        super(Finder, self).__init__()
        self.url = url
        self.searchers = [XPathSearch, CSSSearch, LinkSearch, AnchorTextSearch]


    def _fetch_url(self, url):
        print 'Fetching %s' % url
        r = requests.get(url)
        if r.status_code != 200:
            # Log
            return None

        return r.content

    def process_url(self, publisher_name):
        """

        """
        from ckanext.linkfinder.model import Ruleset

        rules = Ruleset.find(publisher_name, self.url )
        if not rules:
            # Log
            return None

        pagetext = self._fetch_url(self.url)

        # If we have a follow link, try and find a link with a matching href on the page
        # and follow it, overwriting the page content.
        if rules.follow_link:
            r = re.compile(rules.follow_link)
            page = fromstring(pagetext)
            nodes = CSSSearch().process(page, [], 'a')
            for node in nodes:
                href = node.get('href')
                if href and r.match(href):
                    href = urljoin(self.url, href)  # Will return href if it includes proto://host..
                    pagetext = self._fetch_url(href)
                    break

        cfg = {'xpath': rules.xpath,
               'css': rules.css,
               'link': rules.link_regex,
               'anchortext': rules.link_text_regex}

        results = self.search(pagetext, cfg)
        if not rules.allow_multiple:
            results = [results[0]]
        return results

    def search(self, pagetext, config):
        """

        """
        page = fromstring(pagetext)
        nodes = []

        for searcher in self.searchers:
            config_key = searcher.__name__.lower().replace('search', '')
            option = config.get(config_key, {})
            if option:
                nodes = searcher().process(page, nodes, option)

        result = []
        for node in nodes:
            u = urljoin(self.url, node.get('href') or '')
            result.append((node.text_content(), u))

        return result


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
        nodelist.extend(page.cssselect(config) or [])
        return nodelist


class LinkSearch(object):

    def process(self, page, nodelist, config):
        """
        Apply the regex in config to all node hrefs in the nodelist
        """
        r = re.compile(config)
        nodelist = filter(lambda x: r.match(x.get('href') or ''), [node for node in nodelist])
        return nodelist


class AnchorTextSearch(object):

    def process(self, page, nodelist, config):
        """
        Apply the regex in config to all node text in the nodelist
        """
        nodelist.append('Anchor')
        return nodelist
