# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import six
import scrapy
from scrapy.exporters import BaseItemExporter
from scrapy.utils.python import to_bytes
import pprint


class PprintItemExporter(BaseItemExporter):
    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file

    def export_item(self, item):
        serialized = self.serialize_value(item)
        self.file.write(to_bytes(pprint.pformat(serialized).decode('unicode-escape') + '\n'))

    def serialize_value(self, item):
        if isinstance(item, scrapy.Item):
            element = getattr(item, 'item_name', item.__class__.__name__)
            return {
                element: {
                    name: self.serialize_value(value)
                    for name, field, value in self.iter_field_values(item)
                }
            }

        iterator = self.iter_dictlike(item)
        if iterator:
            return {
                name: self.serialize_value(value)
                for name, value in iterator
            }

        iterator = self.iter_listlike(item)
        if iterator:
            return [
                self.serialize_value(value)
                for value in iterator
            ]

        return item

    def iter_field_values(self, item):
        fields = getattr(item, 'fields', {})
        for name, field in fields.iteritems():
            try:
                value = item[name]
            except KeyError:
                continue

            field_name = field.get('name', name)
            serializer = field.get('serializer', lambda arg: arg)
            yield field_name, field, serializer(value)

    def iter_dictlike(self, item):
        try:
            return six.iteritems(item)
        except AttributeError:
            # iteritems できない
            return None

    def iter_listlike(self, item):
        if isinstance(item, (six.string_types, bytes)):
            return None

        try:
            return iter(item)
        except TypeError:
            # iter できない
            return None
