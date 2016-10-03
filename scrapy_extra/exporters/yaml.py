# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from scrapy.utils.python import to_bytes
from .pp import PprintItemExporter
from ..utils import yaml


class YamlLinesItemExporter(PprintItemExporter):
    def __init__(self, file, spider, **kwargs):
        exporter_settings = spider.settings.get('FEED_YAMLLINESITEMEXPORTER_PARAMS', None) or {}
        self.multiple = exporter_settings.get('multiple', False)
        self._configure(kwargs, dont_fail=True)
        self.file = file
        self.first_item = True

    def start_exporting(self):
        self.file.write(b"---\n")

    def export_item(self, item):
        if self.first_item:
            self.first_item = False
        elif self.multiple:
            self.file.write(b"---\n")

        serialized = self.serialize_value(item)
        if not self.multiple:
            serialized = [serialized]
        self.file.write(to_bytes(yaml.safe_dump(serialized, allow_unicode=True)))
