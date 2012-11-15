import re
import csv
import sys
import logging
import operator
import collections
from ckan.lib.base import (BaseController, c, g, render, request, response, abort)

import sqlalchemy
from sqlalchemy import func, cast, Integer
import ckan.model as model


log = logging.getLogger('ckanext.linkfinder')




class GaReport(BaseController):

    def index(self):

        return render('linkfinder/index.html')


