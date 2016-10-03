# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from scrapy.utils.python import to_bytes
from .pp import PprintItemExporter
from ..utils.json import JSONEncoder as ExporterJSONEncoder


class JsonLinesItemExporter(PprintItemExporter):
    def __init__(self, file, spider, **kwargs):
        exporter_settings = spider.settings.get('FEED_JSONLINESITEMEXPORTER_PARAMS', None) or {}
        self._configure(kwargs, dont_fail=True)
        ensure_ascii = exporter_settings.get('ensure_ascii', True)
        self.encoder = ExporterJSONEncoder(ensure_ascii=ensure_ascii)
        self.file = file

    def export_item(self, item):
        serialized = self.serialize_value(item)
        self.file.write(to_bytes(self.encoder.encode(serialized)) + '\n')
