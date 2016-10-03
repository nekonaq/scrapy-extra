# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import


def make_item_loader_method(item_loader_class):

    @classmethod
    def get_item_loader(cls, **kwargs):
        item = kwargs.pop('item', None) or cls()
        return item_loader_class(item=item, **kwargs)

    return get_item_loader
