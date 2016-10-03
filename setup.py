# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re
import os


version = re.search("__version__ = '([^']+)'", open(
    os.path.join(os.path.dirname(__file__), 'scrapy_extra/__init__.py')
    ).read().strip()).group(1)

setup(
    name='scrapy-extra',
    version=version,
    description="extra modules for scrapy",
    author="Tatsuo Nakajyo",
    author_email="tnak@nekonaq.com",
    license='BSD',
    packages=find_packages(),
    install_requires=['scrapy', 'pyyaml', 'six', 'pytz', 'tzlocal'],
    )
