from nose.tools import assert_equal
from ckanext.linkfinder.model import init_tables, Ruleset
from ckanext.linkfinder.lib.finder import Finder
from ckanext.linkfinder.tests.test_base import create_test_data, clean_test_data

class TestFinder(object):

    @classmethod
    def setup_class(cls):
        create_test_data()

    @classmethod
    def teardown_class(cls):
        clean_test_data()

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

    def test_find_ruleset(self):
        print Ruleset.find_for_url('http://www.ons.gov.uk/ons/rel/social-trends-rd/social-trends/no--31--2001-edition/index.html')
