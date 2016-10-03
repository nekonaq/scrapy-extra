# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from twisted.python.failure import Failure
from scrapy.utils.request import referer_str
from scrapy.logformatter import (
    CRAWLEDMSG as ScrapyCRAWLEDMSG,
    SCRAPEDMSG as ScrapySCRAPEDMSG,
    DROPPEDMSG as ScrapyDROPPEDMSG,
    LogFormatter as ScrapyLogFormatter,
)


class LogFormatter(ScrapyLogFormatter):
    def __init__(self, crawledmsg=None, scrapedmsg=None, droppedmsg=None):
        self.crawledmsg = crawledmsg
        if not crawledmsg:
            self.crawled = self._no_logging

        self.scrapedmsg = scrapedmsg
        if not scrapedmsg:
            self.scraped = self._no_logging

        self.droppedmsg = droppedmsg
        if not droppedmsg:
            self.dropped = self._no_logging

    def _no_logging(self, *args):
        return {
            'level': logging.NOTSET,
            'msg': None,
            'args': {},
        }

    def crawled(self, request, response, spider):
        flags = ' %s' % str(response.flags) if response.flags else ''
        return {
            'level': logging.DEBUG,
            'msg': self.crawledmsg,
            'args': {
                'status': response.status,
                'request': request,
                'referer': referer_str(request),
                'flags': flags,
            }
        }

    def scraped(self, item, response, spider):
        if isinstance(response, Failure):
            src = response.getErrorMessage()
        else:
            src = response
        return {
            'level': logging.DEBUG,
            'msg': self.scrapedmsg,
            'args': {
                'src': src,
                'item': item,
            }
        }

    def dropped(self, item, exception, response, spider):
        return {
            'level': logging.WARNING,
            'msg': self.droppedmsg,
            'args': {
                'exception': exception,
                'item': item,
            }
        }

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawledmsg=(
                crawler.settings.getbool('LOG_CRAWLED_ENABLED', True) and
                crawler.settings.get('LOG_CRAWLED_FORMAT', ScrapyCRAWLEDMSG)),
            scrapedmsg=(
                crawler.settings.getbool('LOG_SCRAPED_ENABLED', True) and
                crawler.settings.get('LOG_SCRAPED_FORMAT', ScrapySCRAPEDMSG)),
            droppedmsg=(
                crawler.settings.getbool('LOG_DROPPED_ENABLED', True) and
                crawler.settings.get('LOG_DROPPED_FORMAT', ScrapyDROPPEDMSG)),
        )
