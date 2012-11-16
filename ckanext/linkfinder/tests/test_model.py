from nose.tools import assert_equal

from ckanext.linkfinder.model import init_tables
from ckanext.linkfinder.lib.finder import Finder

class TestFinder:

    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_skip_all(self):
        """
        """
        config = {'xpath': '',
                  'css': '',
                  'link': '',
                  'anchortext': ''}


        links = Finder().search("<html>", config)
        assert len(links) == 0, links

    def test_skip_xpath(self):
        """
        """
        config = {'xpath': '',
                  'css': 'a',
                  'link': '//',
                  'anchortext': '//'}


        links = Finder().search("<html><a href='http://localhost'>Test</a>", config)
        assert len(links) == 3, links