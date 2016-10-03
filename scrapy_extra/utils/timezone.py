# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from scrapy.utils.project import get_project_settings
import pytz

try:
    import tzlocal
except ImportError:
    tzlocal = None


def get_timezone(settings=None, name=None):
    settings = settings or get_project_settings()
    tzname = settings.get(name or 'TIME_ZONE')
    if tzname:
        return pytz.timezone(tzname)
    if tzlocal:
        return tzlocal.get_localzone()
    return pytz.utc
