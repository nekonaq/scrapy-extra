# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import datetime
import pytz
from twisted.internet import defer
from scrapy.utils.log import failure_to_exc_info
from scrapy.utils.misc import load_object
from scrapy.utils.python import get_func_args
from scrapy.extensions.feedexport import (
    logger,
    SpiderSlot as scrapySpiderSlot,
    FeedExporter as scrapyFeedExporter,
)
from ..utils.timezone import get_timezone


class SpiderSlot(scrapySpiderSlot):
    pass


class FeedExporter(scrapyFeedExporter):
    def __init__(self, settings):
        super(FeedExporter, self).__init__(settings)
        self.item_names = settings.getlist('FEED_STORE_ITEMS', [])

        # self.store_empty が False の場合、エクスポートしたアイテム数がゼロである slot は
        # finish_exporting() しない。
        #
        # FEED_STORE_ITEMS の指定がある場合は store_empty = True にすることで、
        # FEED_STORE_ITEMS で生成した slot が finish_exporting() されず、結果として slot の
        # 出力先でクローズされない事態を防ぐ。
        #
        self.store_empty = self.store_empty or bool(self.item_names)

        def _item_uripar(feedexporter, item, spider, **kwargs):
            return kwargs

        item_uripar = settings['FEED_ITEM_URI_PARAMS']
        self._item_uripar = load_object(item_uripar) if item_uripar else _item_uripar

        self.slots = {}
        self.item2uri = {}

    def get_slot(self, spider, **kwargs):
        kwargs.update(self.uri_params)
        if self.urifmt.find('%(') >= 0:
            uri = self.urifmt % kwargs
        else:
            uri = self.urifmt.format(**kwargs)

        try:
            return self.slots[uri]
        except KeyError:
            pass

        storage = self._get_storage(uri)
        file = storage.open(spider)
        exporter = self._get_exporter(
            spider,
            file=file,
            fields_to_export=self.export_fields,
            encoding=self.export_encoding)
        exporter.start_exporting()
        self.slots[uri] = slot = SpiderSlot(file, exporter, storage, uri)
        return slot

    def open_spider(self, spider):
        self.uri_params = self._get_uri_params(spider)
        for item_name in self.item_names:
            slot = self.get_slot(spider, item_name=item_name)
            self.item2uri[item_name] = slot.uri

    def close_spider(self, spider):
        deferreds = []
        for uri, slot in self.slots.iteritems():
            if not slot.itemcount and not self.store_empty:
                continue
            slot.exporter.finish_exporting()

            logfmt = "%(format)s feed (%(itemcount)d items) in: %(uri)s"
            log_args = {
                'format': self.format,
                'itemcount': slot.itemcount,
                'uri': slot.uri,
            }

            d = defer.maybeDeferred(slot.storage.store, slot.file)

            d.addCallback(lambda _: logger.info(
                "Stored {}".format(logfmt),
                log_args,
                extra={'spider': spider}))

            d.addErrback(lambda f: logger.error(
                "Error storing {}".format(logfmt),
                log_args,
                exc_info=failure_to_exc_info(f),
                extra={'spider': spider}))

            deferreds.append(d)

        if deferreds:
            return defer.DeferredList(deferreds)

    def item_scraped(self, item, spider):
        if item is None:
            return

        item_name = getattr(item, 'item_name', None) or item.__class__.__name__
        uri = self.item2uri.get(item_name, None)
        if uri:
            slot = self.slots[uri]
        else:
            params = self._item_uripar(self, item, spider, item_name=item_name)
            slot = self.get_slot(spider, **params)

        slot.exporter.export_item(item)
        slot.itemcount += 1
        return item

    def _get_exporter(self, spider, **kwargs):
        exporter = self.exporters[self.format]
        if 'spider' in get_func_args(exporter):
            kwargs['spider'] = spider
        return self.exporters[self.format](**kwargs)

    TIMESTAMP_FORMAT = '%Y-%m-%dT%H-%M-%S'

    def _get_uri_params(self, spider):
        params = {}
        for k in dir(spider):
            params[k] = getattr(spider, k)
        tz = get_timezone()
        utcnow = datetime.datetime.utcnow().replace(microsecond=0, tzinfo=pytz.utc)
        params['_utcnow'] = utcnow
        params['time'] = utcnow.strftime(self.TIMESTAMP_FORMAT)
        params['timelocal'] = tz.normalize(utcnow).strftime(self.TIMESTAMP_FORMAT)
        self._uripar(params, spider)
        return params
