##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests of ZConfig.loader classes and helper functions."""

import os.path
import sys
import unittest

from StringIO import StringIO

import ZConfig
import ZConfig.loader
import ZConfig.url

from ZConfig.tests.test_config import CONFIG_BASE


try:
    myfile = __file__
except NameError:
    myfile = sys.argv[0]

myfile = os.path.abspath(myfile)
LIBRARY_DIR = os.path.join(os.path.dirname(myfile), "library")


class LoaderTestCase(unittest.TestCase):

    def test_schema_caching(self):
        loader = ZConfig.loader.SchemaLoader()
        url = ZConfig.url.urljoin(CONFIG_BASE, "simple.xml")
        schema1 = loader.loadURL(url)
        schema2 = loader.loadURL(url)
        self.assert_(schema1 is schema2)

    def test_schema_components(self):
        loader = ZConfig.loader.SchemaLoader()
        url = ZConfig.url.urljoin(CONFIG_BASE, "library.xml")
        schema = loader.loadURL(url)
        type_a = loader.loadURL(url + "#type-a")
        type_b = loader.loadURL(url + "#type-b")
        self.assertEqual(type_a.name, "type-a")
        self.assertEqual(type_b.name, "type-b")
        # make sure we're using the cached schema for the types
        self.assert_(type_a is schema.gettype("type-a"))
        self.assert_(type_b is schema.gettype("type-b"))

    def test_simple_import_with_cache(self):
        loader = ZConfig.loader.SchemaLoader()
        url1 = ZConfig.url.urljoin(CONFIG_BASE, "library.xml")
        schema1 = loader.loadURL(url1)
        sio = StringIO("<schema>"
                       "  <import src='library.xml'/>"
                       "  <section type='type-a' name='section'/>"
                       "</schema>")
        url2 = ZConfig.url.urljoin(CONFIG_BASE, "stringio")
        schema2 = loader.loadFile(sio, url2)
        self.assert_(schema1.gettype("type-a") is schema2.gettype("type-a"))

    def test_import_errors(self):
        # must specify exactly one of package or src
        self.assertRaises(ZConfig.SchemaError, ZConfig.loadSchemaFile,
                          StringIO("<schema><import/></schema>"))
        self.assertRaises(ZConfig.SchemaError, ZConfig.loadSchemaFile,
                          StringIO("<schema>"
                                   "  <import src='library.xml'"
                                   "          package='ZConfig'/>"
                                   "</schema>"))

    def test_import_from_package(self):
        loader = ZConfig.loader.SchemaLoader(library=LIBRARY_DIR)
        sio = StringIO("<schema>"
                       "  <import package='widget'/>"
                       "</schema>")
        schema = loader.loadFile(sio)
        self.assert_(schema.gettype("widget-a") is not None)

    def test_import_from_package_extended(self):
        loader = ZConfig.loader.SchemaLoader(library=LIBRARY_DIR)
        sio = StringIO("<schema>"
                       "  <import package='thing'/>"
                       "  <section name='*' type='thing' attribute='thing'/>"
                       "</schema>")
        schema = loader.loadFile(sio)
        schema.gettype("thing")
        schema.gettype("thing-a")
        schema.gettype("thing-b")
        schema.gettype("thing-ext")

        # Make sure the extension is wired in properly:
        sio = StringIO("<thing-ext thing/>")
        conf, handlers = ZConfig.loadConfigFile(schema, sio)
        self.assertEqual(conf.thing.thing_ext_key, "thing-ext-default")

    def test_urlsplit_urlunsplit(self):
        # Extracted from Python's test.test_urlparse module:
        for url, parsed, split in [
            ('http://www.python.org',
             ('http', 'www.python.org', '', '', '', ''),
             ('http', 'www.python.org', '', '', '')),
            ('http://www.python.org#abc',
             ('http', 'www.python.org', '', '', '', 'abc'),
             ('http', 'www.python.org', '', '', 'abc')),
            ('http://www.python.org/#abc',
             ('http', 'www.python.org', '/', '', '', 'abc'),
             ('http', 'www.python.org', '/', '', 'abc')),
            ("http://a/b/c/d;p?q#f",
             ('http', 'a', '/b/c/d', 'p', 'q', 'f'),
             ('http', 'a', '/b/c/d;p', 'q', 'f')),
            ('file:///tmp/junk.txt',
             ('file', '', '/tmp/junk.txt', '', '', ''),
             ('file', '', '/tmp/junk.txt', '', '')),
            ]:
            result = ZConfig.url.urlsplit(url)
            self.assertEqual(result, split)
            result2 = ZConfig.url.urlunsplit(result)
            self.assertEqual(result2, url)


def test_suite():
    return unittest.makeSuite(LoaderTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
