import logging
import datetime
import os

from .model import init_tables

from pylons import config
from ckan.lib.cli import CkanCommand
# No other CKAN imports allowed until _load_config is run,
# or logging is disabled

class InitDB(CkanCommand):
    """
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 0
    min_args = 0

    def __init__(self, name):
        super(InitDB, self).__init__(name)

    def command(self):
        """
        """
        self._load_config()
        log = logging.getLogger(__name__)

        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        import ckanext.linkfinder.model as lf_model
        lf_model.init_tables()
        log.debug("DB tables are setup")


class CheckLinks(CkanCommand):
    """
    Reads from the provided input file where one line contains one url
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 1

    def __init__(self, name):
        super(CheckLinks, self).__init__(name)

    def command(self):
        """
        """
        from ckanext.linkfinder.lib.finder import Finder
        from ckanext.linkfinder.tests.test_base import create_test_data, clean_test_data

        self._load_config()
        log = logging.getLogger(__name__)

        input_file = self.args[0]
        if not os.path.exists(input_file):
            log.error("Could not open specified input file %s" % input_file)
            return

        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        create_test_data()

        log.info('Reading links')
        with open(input_file, 'r') as f:
            for line in f.readlines():
                publisher,url = line.split('=')
                log.info(" - Checking %s (%s)" % (publisher,url))
                p = Finder(url.strip()).process_url(publisher)
                print p


        clean_test_data()