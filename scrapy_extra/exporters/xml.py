# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import sys
import six
import scrapy
from contextlib import contextmanager
from xml.sax.saxutils import XMLGenerator
from .pp import PprintItemExporter


class XmlSerializer(object):
    root_element = object()

    @classmethod
    @contextmanager
    def create(cls, xg, encoding=None):
        instance = cls(xg, cls.root_element, encoding=encoding)
        yield instance
        instance.finalize()

    def __init__(self, xg, element, encoding=None):
        self.xg = xg
        self.encoding = encoding

        self.element = element
        self.attrs = {}
        self.children = []
        self.text = None
        self.cdata = False

    def finalize(self):
        if self.element == self.root_element:
            for child in self.children:
                child.flush()

    def flush(self):
        element = self.element

        if element == self.root_element:
            self.finalize()
            return

        if element:
            self.xg.startElement(element, self.attrs)

        text = self.text
        if text:
            if not isinstance(text, six.text_type):
                text = str(text)

            if self.cdata:
                self.xg.ignorableWhitespace('<![CDATA[{}]]>'.format(text))
            else:
                self._xg_characters(text)

        for child in self.children:
            child.flush()

        if self.element:
            self.xg.endElement(element)

    @contextmanager
    def add_element(self, element):
        instance = type(self)(self.xg, element, encoding=self.encoding)
        self.children.append(instance)
        yield instance
        instance.finalize()

    def set_text(self, text, cdata=False):
        self.text = text
        self.cdata = cdata

    # Workaround for http://bugs.python.org/issue17606
    # Before Python 2.7.4 xml.sax.saxutils required bytes;
    # since 2.7.4 it requires unicode. The bug is likely to be
    # fixed in 2.7.6, but 2.7.6 will still support unicode,
    # and Python 3.x will require unicode, so ">= 2.7.4" should be fine.
    if sys.version_info[:3] >= (2, 7, 4):
        def _xg_characters(self, serialized_value):
            if not isinstance(serialized_value, six.text_type):
                serialized_value = serialized_value.decode(self.encoding)
            return self.xg.characters(serialized_value)
    else:  # pragma: no cover
        def _xg_characters(self, serialized_value):
            return self.xg.characters(serialized_value)


class XmlItemExporter(PprintItemExporter):
    def __init__(self, file, spider, **kwargs):
        exporter_settings = spider.settings.get('FEED_XMLITEMEXPORTER_PARAMS', None) or {}
        self.root_element = exporter_settings.get('root_element', 'items')
        self.item_element = {
            'dict': exporter_settings.get('item_element', 'item'),
            'list': exporter_settings.get('list_element', 'values'),
            'value': exporter_settings.get('value_element', 'value'),
            }
        self._configure(kwargs, dont_fail=True)
        self.encoding = exporter_settings.get('encoding', self.encoding) or 'utf-8'
        self.xg = XMLGenerator(file, encoding=self.encoding)

    def start_exporting(self):
        self.xg.startDocument()
        self.xg.startElement(self.root_element, {})

    def finish_exporting(self):
        self.xg.endElement(self.root_element)
        self.xg.endDocument()

    def export_item(self, item):
        with XmlSerializer.create(self.xg, encoding=self.encoding) as xs:
            self.serialize_value(item, xs, item_element=self.item_element)

    def serialize_value(self, item, xs, item_element=None, cdata=False, inline=None):
        if item is None:
            # do not export_empty_items
            return

        if isinstance(item, scrapy.Item):
            element = getattr(item, 'item_name', item.__class__.__name__)
            with xs.add_element(element) as xsp:
                iterator = self.iter_field_values(item)
                for name, field, value in iterator:
                    attrib = field.get('attrib')
                    if attrib == 'text':
                        xsp.set_text(value)
                        continue

                    if attrib == 'cdata':
                        with xsp.add_element(name) as xspp:
                            self.serialize_value(value, xspp, cdata=True)
                        continue

                    if attrib:
                        xsp.attrs[name] = value
                        continue

                    if field.get('inline', False):
                        self.serialize_value(value, xsp, inline=name)
                        continue

                    with xsp.add_element(name) as xspp:
                        self.serialize_value(value, xspp)
            return

        if inline:
            item_element = {'dict': inline, 'value': inline}
            item_element_listvalue = {'dict': inline, 'list': inline, 'value': inline}
        else:
            item_element = item_element or {}
            item_element_listvalue = self.item_element

        iterator = self.iter_dictlike(item)
        if iterator:
            with xs.add_element(item_element.get('dict')) as xsp:
                for name, value in iterator:
                    with xsp.add_element(name) as xspp:
                        self.serialize_value(value, xspp)
            return

        iterator = self.iter_listlike(item)
        if iterator:
            with xs.add_element(item_element.get('list')) as xsp:
                for value in iterator:
                    self.serialize_value(value, xsp, item_element=item_element_listvalue)
            return

        with xs.add_element(item_element.get('value')) as xsp:
            xsp.set_text(item, cdata=cdata)
