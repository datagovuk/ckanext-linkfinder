import logging
import datetime
import os
import re
import time

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
        from ckanext.linkfinder.lib.ons_scraper import scrape_ons_publication
        self._load_config()
        log = logging.getLogger(__name__)

        import ckan.model as model
        model.Session.remove()
        model.Session.configure(bind=model.meta.engine)
        model.repo.new_revision()

        if len(self.args) == 1:
            print 'Fetching %s' % self.args[0]
            datasets = [model.Package.get(self.args[0])]
        else:
            # For some reason the resourcegroup object is in between datasets
            # and its resources, which makes doing a regex on the query rather
            # painful.
            datasets = model.Session.query(model.Package)\
                .join(model.PackageExtra)\
                .filter(model.PackageExtra.key=="external_reference")\
                .filter(model.PackageExtra.value=="ONSHUB")\
                .order_by('package.name desc').all()

        def chunk(n, l):
            for i in xrange(0, len(l), n):
                yield l[i:i+n]

        counter = 0
        resource_count = 0
        for dataset_chunk in chunk(100, datasets):
            log.info('Processing next chunk of 100')
            for dataset in dataset_chunk:
                added = False
                time.sleep(1)

                new_resources = scrape_ons_publication(dataset)
                if new_resources:
                    counter = counter + 1

                    for r in new_resources:
                        # Check if the URL already appears in the dataset's
                        # resources, and if so then skip it.
                        matched = [x for x in dataset.resources if x.url == r['url']]
                        if matched:
                            log.error("The URL for this resource was already found in this dataset")
                            continue

                        resource_count = resource_count + 1
                        dataset.add_resource(r['url'],
                                             description=r['description'],
                                             format=r['url'][-3:],
                                             name=r['title'])

                        if self.options.delete_resources:
                            log.info("Marking resource %s as deleted" % (r['original'],))
                            r['original'].state = 'deleted'
                            model.Session.add(r['original'])

                        added = True

                if added:
                    model.Session.add(dataset)
            model.Session.commit()

        print "Processed %d datasets" % (counter)
        print "Added %d resources" % (resource_count)

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
