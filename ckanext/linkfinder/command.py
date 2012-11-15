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
        self.log = logging.getLogger("ckanext.linkfinder")

    def command(self):
        """
        """
        self._load_config()

        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        import ckanext.linkfinder.model as lf_model
        lf_model.init_tables()
        self.log.debug("DB tables are setup")


class CheckLinks(CkanCommand):
    """
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 0

    def __init__(self, name):
        super(CheckLinks, self).__init__(name)
        self.log = logging.getLogger('ckanext.linkfinder')
        self.parser.add_option('-d', '--debug',
                               action='store_true',
                               default=False,
                               dest='debug',
                               help='Debug mode, does not write anything to the DB ')

    def command(self):
        """
        """
        self._load_config()

        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)

        self.log.info('Checking links')