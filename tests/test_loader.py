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

import unittest
import urlparse

from StringIO import StringIO

import ZConfig
import ZConfig.loader

from ZConfig import url

from ZConfig.tests.test_config import CONFIG_BASE


class LoaderTestCase(unittest.TestCase):

    def test_schema_caching(self):
        loader = ZConfig.loader.SchemaLoader()
        url = urlparse.urljoin(CONFIG_BASE, "simple.xml")
        schema1 = loader.loadURL(url)
        schema2 = loader.loadURL(url)
        self.assert_(schema1 is schema2)

    def test_schema_components(self):
        loader = ZConfig.loader.SchemaLoader()
        url = urlparse.urljoin(CONFIG_BASE, "library.xml")
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
        url1 = urlparse.urljoin(CONFIG_BASE, "library.xml")
        schema1 = loader.loadURL(url1)
        sio = StringIO("<schema>"
                       "  <import src='library.xml'/>"
                       "  <section type='type-a' name='section'/>"
                       "</schema>")
        url2 = urlparse.urljoin(CONFIG_BASE, "stringio")
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


def test_suite():
    return unittest.makeSuite(LoaderTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
