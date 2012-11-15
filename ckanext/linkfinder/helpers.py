import logging
import operator

import ckan.lib.base as base
import ckan.model as model
from ckan.logic import get_action

from ckanext.ga_report.ga_model import GA_Url, GA_Publisher
from ckanext.ga_report.controller import _get_publishers
_log = logging.getLogger(__name__)

