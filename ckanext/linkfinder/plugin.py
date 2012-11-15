import logging
import ckan.lib.helpers as h
import ckan.plugins as p
from ckan.plugins import implements, toolkit

#from ckanext.linkfinder.helpers import ()

log = logging.getLogger('ckanext.linkfinder')

class LinkFinderPlugin(p.SingletonPlugin):
    implements(p.IConfigurer, inherit=True)
    implements(p.IRoutes, inherit=True)
    implements(p.ITemplateHelpers, inherit=True)

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')

    def get_helpers(self):
        """
        A dictionary of extra helpers that will be available to provide
        ga report info to templates.
        """
        return {
            'linkfinder_installed': lambda: True,
        }

    def after_map(self, map):
        """
        map.connect(
            '/data/site-usage',
            controller='ckanext.ga_report.controller:GaReport',
            action='index'
        )
        map.connect(
            '/data/site-usage/data_{month}.csv',
            controller='ckanext.ga_report.controller:GaReport',
            action='csv'
        )

        # GaDatasetReport
        map.connect(
            '/data/site-usage/publisher',
            controller='ckanext.ga_report.controller:GaDatasetReport',
            action='publishers'
        )
        map.connect(
            '/data/site-usage/publishers_{month}.csv',
            controller='ckanext.ga_report.controller:GaDatasetReport',
            action='publisher_csv'
        )
        map.connect(
            '/data/site-usage/dataset/datasets_{id}_{month}.csv',
            controller='ckanext.ga_report.controller:GaDatasetReport',
            action='dataset_csv'
        )
        map.connect(
            '/data/site-usage/dataset',
            controller='ckanext.ga_report.controller:GaDatasetReport',
            action='read'
        )
        map.connect(
            '/data/site-usage/dataset/{id}',
            controller='ckanext.ga_report.controller:GaDatasetReport',
            action='read_publisher'
        )
        """
        return map

