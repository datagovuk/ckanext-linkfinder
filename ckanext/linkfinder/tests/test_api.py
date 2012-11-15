import os
import datetime
from nose.tools import assert_equal
from ckanext.linkfinder.model import init_tables

class TestAPI:

    @classmethod
    def setup_class(cls):
        init_tables()

    @classmethod
    def teardown_class(cls):
        pass
