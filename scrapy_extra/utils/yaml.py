# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import yaml

try:
    from yaml import (
        CDump as Dumper,
        CSafeDumper as SafeDumper,
        CLoader as Loader,
        CSafeLoader as SafeLoader,
        )
except ImportError:
    from yaml import (
        Dumper,
        SafeDumper,
        Loader,
        SafeLoader
        )


def dump(data, stream=None, Dumper=Dumper, **kwds):
    return yaml.dump(data, stream=stream, Dumper=Dumper, **kwds)


def dump_all(documents, stream=None, Dumper=Dumper, **kwds):
    return yaml.dump_all(documents, stream=stream, Dumper=Dumper, **kwds)


def safe_dump_all(documents, stream=None, **kwds):
    return yaml.dump_all(documents, stream, Dumper=SafeDumper, **kwds)


def safe_dump(data, stream=None, **kwds):
    return yaml.dump_all([data], stream, Dumper=SafeDumper, **kwds)


def load(stream, Loader=Loader):
    return yaml.load(stream, Loader=Loader)


def load_all(stream, Loader=Loader):
    return yaml.load_all(stream, Loader=Loader)


def safe_load(stream):
    return load(stream, SafeLoader)


def safe_load_all(stream):
    return load_all(stream, SafeLoader)
