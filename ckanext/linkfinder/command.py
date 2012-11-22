import logging
import datetime
import os
import re
import time
import sys

from .model import init_tables

from pylons import config
from ckan.lib.cli import CkanCommand
# No other CKAN imports allowed until _load_config is run,
# or logging is disabled


class ONSUpdateTask(CkanCommand):
    """
    Runs a one-off task to fetch more accurate resource links for ONS datasets
    """
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 1
    min_args = 0

    def __init__(self, name):
        super(ONSUpdateTask, self).__init__(name)
        self.parser.add_option('-d', '--delete-resources',
                               action='store_true',
                               default=False,
                               dest='delete_resources',
                               help='If specified, old resources that are replaced will be deleted')



    def command(self):
        """
        """
        import ckanclient
        from ckanext.linkfinder.lib.ons_scraper import scrape_ons_publication
        from ckan.logic import get_action

        self._load_config()
        log = logging.getLogger(__name__)

        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)
        model.repo.new_revision()

        site_user = get_action('get_site_user')({'model': model, 'ignore_auth': True}, {})
        apikey = site_user['apikey']

        ckan = ckanclient.CkanClient(base_location='%sapi' % config['ckan.site_url'],
                                     api_key=apikey)

        opts = {'external_reference': 'ONSHUB', 'offset': 0, 'limit': 10000}
        q = ''
        if len(self.args) == 1:
            q = self.args[0].replace(',', '')

        search_results = ckan.package_search(q, opts)
        log.debug("There are %d results" % search_results['count'])
        datasets = search_results['results']

        counter = 0
        resource_count = 0
        for dsname in datasets:
            dataset = ckan.package_entity_get(dsname)
            counter = counter + 1
            added = False
            time.sleep(0.5)

            log.info('Processing %s' % (dsname,))

            new_resources = scrape_ons_publication(dataset)
            if new_resources:
                # Update the fold resources, if they need to have their type set.
                for r in dataset['resources']:
                    r['resource_type'] = 'documentation'

                # Save the update to the resources for this dataset
                ckan.package_entity_put(dataset)

                for r in new_resources:
                    # Check if the URL already appears in the dataset's
                    # resources, and if so then skip it.
                    existing = [x for x in dataset['resources'] if x['url'] == r['url']]
                    if existing:
                        log.error("The URL for this resource was already found in this dataset")
                        continue

                    resource_count = resource_count + 1
                    ckan.add_package_resource(dataset['name'], r['url'],
                                              resource_type='data',
                                              format=r['url'][-3:],
                                              description=r['description'],
                                              name=r['title'])

                    added = True

        log.info("Processed %d datasets" % (counter))
        log.info( "Added %d resources" % (resource_count))

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

        clean_test_data()

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
