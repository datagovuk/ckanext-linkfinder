import re
import logging
import requests
import uuid
from urlparse import urljoin
from lxml.html import fromstring
import ckan.model as model


url_regex = re.compile('^http://www.ons.gov.uk/ons/.*$')
follow_regex = re.compile('^.*ons/publications/re-reference-tables.html.*$')

def scrape_ons_publication(dataset):
    """
    Narrows down the datasets, and resources that can be scraped
    and processed by this scraper.
    """
    resources = []
    for resource in dataset['resources']:
        if url_regex.match(resource['url']):
            resources.append(resource)

    if not resources:
        return None

    return filter(None, [_process_ons_resource(dataset,r) for r in resources] )

def _log(line, err_msg):
    pass

def _process_ons_resource(dataset, resource):
    log = logging.getLogger(__name__)

    results = []
    line = {"dataset": dataset, "resource": resource, "url": resource['url']}

    # Get the first page that we were pointed at.
    r = requests.get(resource['url'])
    line["status code"] = r.status_code
    if r.status_code <> 200:
        log.error("Failed to fetch %s, got status %s" % (resource['url'], r.status_code))
        _log(line, "HTTP error")
        return None

    # need to follow the link to the data page. Somewhere on the page is a link
    # that looks like ^.*ons/publications/re-reference-tables.html.*$
    if not r.content:
        log.debug("Successfully fetched %s but page was empty" % (resource['url'],))
        _log(line, "Page was empty")
        return None

    page = fromstring(r.content)
    nodes = page.cssselect('a')
    href = None
    for node in nodes:
        h = node.get('href')
        if h and follow_regex.match(h):
            href = urljoin(resource['url'], h)  # Will return href if it includes proto://host..
            break

    if not href:
        _log(line, "No data page")
        log.debug("Unable to find the 'data' page which contains links to resources")
        return None

    r = requests.get(href)
    if r.status_code <> 200:
        _log(line, "Failed to fetch data page")
        log.error("Failed to fetch data page %s, got status %s" % (resource['url'], r.status_code))
        return None

    log.debug("Found 'data' page content")
    page = fromstring(r.content)
    outerdivs = page.cssselect('.table-info')
    url, title, description = None, None, None

    for odiv in outerdivs:

        # URL
        dldiv = odiv.cssselect('.download-options ul li a')[0]
        url = dldiv.get('href')

        # Title
        dlinfo = odiv.cssselect('.download-info')[0]
        title = dlinfo.cssselect('h3')[0].text_content()

        description = dlinfo.cssselect('div')[2].text_content()
        description = description.strip()[len('Description: '):]

    if not url:
        _log(line, "No link to data page")
        log.info("Could not find a link on the data page at %s" % (href,))
        return None
    else:
        _log(line, "OK")
        log.debug("Found a link on the data page")

    return {'url': urljoin(resource['url'], url),
            'description': description,
            'title': title,
            'original': resource}








