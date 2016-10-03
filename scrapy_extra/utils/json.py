# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import json
import datetime
import decimal
import uuid
from twisted.internet import defer
from scrapy.http import Request, Response
from scrapy.item import BaseItem


class JSONEncoder(json.JSONEncoder):

    # DATE_FORMAT = "%Y-%m-%d"
    # TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            # return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            # return o.strftime(self.DATE_FORMAT)
            return o.isoformat()
        elif isinstance(o, datetime.time):
            # return o.strftime(self.TIME_FORMAT)
            if o.utcoffset() is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, uuid.UUID):
            return str(o)
        elif isinstance(o, defer.Deferred):
            return str(o)
        elif isinstance(o, BaseItem):
            return dict(o)
        elif isinstance(o, Request):
            return "<%s %s %s>" % (type(o).__name__, o.method, o.url)
        elif isinstance(o, Response):
            return "<%s %s %s>" % (type(o).__name__, o.status, o.url)
        else:
            return super(JSONEncoder, self).default(o)
