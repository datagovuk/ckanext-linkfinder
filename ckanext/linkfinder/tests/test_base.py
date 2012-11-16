import os
import ckan.model as model
from ckanext.linkfinder.model import make_uuid, Ruleset

def dbsetup():
    from paste.registry import Registry
    from paste.script.util.logging_config import fileConfig
    from paste.deploy import appconfig
    filename = os.path.abspath("../ckan/development.ini")
    if not os.path.exists(filename):
        raise AssertionError('Config filename %r does not exist.' % filename)
    fileConfig(filename)
    conf = appconfig('config:' + filename)
    assert 'ckan' not in dir() # otherwise loggers would be disabled

    # We have now loaded the config. Now we can import ckan for the
    # first time.
    from ckan.config.environment import load_environment
    load_environment(conf.global_conf, conf.local_conf)


def create_test_data():

    dbsetup()

# http://www.neighbourhood.statistics.gov.uk/dissemination/datasetList.do;jsessionid=21lTQm4GYBLNTHnbnPWynGQxFkjvYMgsx1BRpqTQ14p4QnqNJbyH!563756039!1353070660788?JSAllowed=true&Function=&%24ph=60&CurrentPageId=60&step=1&CurrentTreeIndex=-1&searchString=&datasetFamilyId=1818&Next.x=13&Next.y=11&nsjs=true&nsck=true&nssvg=false&nswid=1154
# http://www.ons.gov.uk/ons/rel/social-trends-rd/social-trends/no--31--2001-edition/index.html
  # http://www.ons.gov.uk/ons/publications/re-reference-tables.html?edition=tcm%3A77-110539

    datadicts = [
        {'id':'test_1', 'publisher_name': 'office-for-national-statistics',
         'url_regex': '^http://www.neighbourhood.statistics.gov.uk/.*$',
         'follow_link': '', 'xpath': '', 'css': '', 'link_regex': '',
         'link_text_regex': '', 'allow_multiple': 0},

        {'id':'test_2', 'publisher_name': 'office-for-national-statistics',
         'url_regex': '^http://www.ons.gov.uk/ons/rel/.*$',
         'follow_link': '^ons/publications/re-reference-tables.html.*$',
         'xpath': '', 'css': '', 'link_regex': '^.*[*.xls|*.csv|*.zip].*$',
         'link_text_regex': '', 'allow_multiple': 0},
    ]
    for data in datadicts:
        if not model.Session.query(Ruleset).filter(Ruleset.url_regex==data['url_regex']).first():
            model.Session.add(Ruleset(**data))
    model.Session.commit()


def clean_test_data():
    model.Session.query(Ruleset).filter(Ruleset.id.like('test_%')).delete(synchronize_session='fetch')
    model.Session.commit()