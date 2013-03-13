from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-linkfinder',
	version=version,
	description="Finds links from resources that are actually pages containing links to the data",
	long_description="""\
	""",
	classifiers=[],
	keywords='',
	author='Ross Jones',
	author_email='ross@servercode.co.uk',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.linkfinder'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		'lxml',
		'cssselect',
		'requests'
	],
	entry_points=\
	"""
        [ckan.plugins]
	    # Add plugins here
	    linkfinder=ckanext.linkfinder.plugin:LinkFinderPlugin

        [paste.paster_command]
        checklinks = ckanext.linkfinder.command:CheckLinks
        initdb = ckanext.linkfinder.command:InitDB
        ons_update_once = ckanext.linkfinder.command:ONSUpdateTask
        onsreport = ckanext.linkfinder.command:ONSReportTask
	""",
)
