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

    def xtest_find_ruleset(self):
        u = 'http://www.ons.gov.uk/ons/rel/ilch/index-of-labour-costs-per-hour--experimental-/q4-2010/index.html'
        p = Finder(u).process_url('office-for-national-statistics')
        assert len(p) == 1, p
        assert p[0][0] == 'Excel', p[0]
        assert p[0][1] == 'http://www.ons.gov.uk/ons/rel/ilch/index-of-labour-costs-per-hour--experimental-/q4-2010/index-of-labour-costs--ilch-.xls'

    def test_find_ruleset(self):
        u = 'http://www.ons.gov.uk/ons/rel/rsi/retail-sales/october-2012/stb-rsi-october-2012.html'
        p = Finder(u).process_url('office-for-national-statistics')
        assert len(p) == 6, p
