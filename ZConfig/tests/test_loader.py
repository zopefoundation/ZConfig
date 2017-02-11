##############################################################################
#
# Copyright (c) 2002, 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests of ZConfig.loader classes and helper functions."""

import os.path
import sys
import tempfile
import unittest

import ZConfig
import ZConfig.loader
import ZConfig.url

from ZConfig._compat import NStringIO as StringIO
from ZConfig._compat import urllib2

from ZConfig.tests.support import CONFIG_BASE, TestHelper


try:
    myfile = __file__
except NameError: # pragma: no cover
    myfile = sys.argv[0]

myfile = os.path.abspath(myfile)
LIBRARY_DIR = os.path.join(os.path.dirname(myfile), "library")


class LoaderTestCase(TestHelper, unittest.TestCase):

    def test_schema_caching(self):
        loader = ZConfig.loader.SchemaLoader()
        url = ZConfig.url.urljoin(CONFIG_BASE, "simple.xml")
        schema1 = loader.loadURL(url)
        schema2 = loader.loadURL(url)
        self.assertTrue(schema1 is schema2)

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
        self.assertTrue(schema1.gettype("type-a") is schema2.gettype("type-a"))

    def test_schema_loader_source_errors(self):
        loader = ZConfig.loader.SchemaLoader()
        self.assertRaisesRegexp(ZConfig.SchemaError,
                                "illegal schema component name",
                                loader.schemaComponentSource,
                                '', None)
        self.assertRaisesRegexp(ZConfig.SchemaError,
                                "illegal schema component name",
                                loader.schemaComponentSource,
                                'foo..bar', None)

    def test_config_loader_abstract_schema(self):
        class MockSchema(object):
            _abstract = True
            def isabstract(self):
                return self._abstract
            def gettype(self, _t):
                return self

        self.assertRaisesRegexp(ZConfig.SchemaError,
                                "abstract type",
                                ZConfig.loader.ConfigLoader,
                                MockSchema())

        s = MockSchema()
        s._abstract = False

        loader = ZConfig.loader.ConfigLoader(s)
        s._abstract = True

        self.assertRaisesRegexp(ZConfig.ConfigurationError,
                                "cannot match abstract section",
                                loader.startSection,
                                None, None, None)

    def test_simple_import_using_prefix(self):
        self.load_schema_text("""\
            <schema prefix='ZConfig.tests.library'>
              <import package='.thing'/>
            </schema>
            """)

    def test_import_errors(self):
        # must specify exactly one of package or src
        self.assertRaises(ZConfig.SchemaError, ZConfig.loadSchemaFile,
                          StringIO("<schema><import/></schema>"))
        self.assertRaises(ZConfig.SchemaError, ZConfig.loadSchemaFile,
                          StringIO("<schema>"
                                   "  <import src='library.xml'"
                                   "          package='ZConfig'/>"
                                   "</schema>"))
        # cannot specify src and file
        self.assertRaises(ZConfig.SchemaError, ZConfig.loadSchemaFile,
                          StringIO("<schema>"
                                   "  <import src='library.xml'"
                                   "          file='other.xml'/>"
                                   "</schema>"))
        # cannot specify module as package
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.test_loader'/>"
                       "</schema>")
        with self.assertRaises(ZConfig.SchemaResourceError) as ctx:
            ZConfig.loadSchemaFile(sio)

        e = ctx.exception
        self.assertEqual(e.filename, "component.xml")
        self.assertEqual(e.package, "ZConfig.tests.test_loader")
        self.assertTrue(e.path is None)
        # make sure the str() doesn't raise an unexpected exception
        str(e)

    def test_import_from_package(self):
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.widget'/>"
                       "</schema>")
        schema = loader.loadFile(sio)
        self.assertTrue(schema.gettype("widget-a") is not None)

    def test_import_from_package_with_file(self):
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.widget'"
                       "          file='extra.xml' />"
                       "</schema>")
        schema = loader.loadFile(sio)
        self.assertTrue(schema.gettype("extra-type") is not None)

    def test_import_from_package_extra_directory(self):
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.thing'"
                       "          file='extras.xml' />"
                       "</schema>")
        schema = loader.loadFile(sio)
        self.assertTrue(schema.gettype("extra-thing") is not None)

    def test_import_from_package_with_missing_file(self):
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.widget'"
                       "          file='notthere.xml' />"
                       "</schema>")
        with self.assertRaises(ZConfig.SchemaResourceError) as ctx:
            loader.loadFile(sio)
        e = ctx.exception
        self.assertEqual(e.filename, "notthere.xml")
        self.assertEqual(e.package, "ZConfig.tests.library.widget")
        self.assertTrue(e.path)
        # make sure the str() doesn't raise an unexpected exception
        str(e)

    def test_import_from_package_with_directory_file(self):
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.widget'"
                       "          file='really/notthere.xml' />"
                       "</schema>")
        self.assertRaises(ZConfig.SchemaError, loader.loadFile, sio)

    def test_import_two_components_one_package(self):
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.widget' />"
                       "  <import package='ZConfig.tests.library.widget'"
                       "          file='extra.xml' />"
                       "</schema>")
        schema = loader.loadFile(sio)
        schema.gettype("widget-a")
        schema.gettype("extra-type")

    def test_import_component_twice_1(self):
        # Make sure we can import a component twice from a schema.
        # This is most likely to occur when the component is imported
        # from each of two other components, or from the top-level
        # schema and a component.
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.widget' />"
                       "  <import package='ZConfig.tests.library.widget' />"
                       "</schema>")
        schema = loader.loadFile(sio)
        schema.gettype("widget-a")

    def test_import_component_twice_2(self):
        # Make sure we can import a component from a config file even
        # if it has already been imported from the schema.
        loader = ZConfig.loader.SchemaLoader()
        sio = StringIO("<schema>"
                       "  <import package='ZConfig.tests.library.widget' />"
                       "</schema>")
        schema = loader.loadFile(sio)
        loader = ZConfig.loader.ConfigLoader(schema)
        sio = StringIO("%import ZConfig.tests.library.widget")
        loader.loadFile(sio)

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

    def test_file_url_normalization(self):
        self.assertEqual(
            ZConfig.url.urlnormalize("file:/abc/def"),
            "file:///abc/def")
        self.assertEqual(
            ZConfig.url.urlunsplit(("file", "", "/abc/def", "", "")),
            "file:///abc/def")
        self.assertEqual(
            ZConfig.url.urljoin("file:/abc/", "def"),
            "file:///abc/def")
        self.assertEqual(
            ZConfig.url.urldefrag("file:/abc/def#frag"),
            ("file:///abc/def", "frag"))

    def test_url_from_file(self):
        class MockFile(object):
            name = 'path'
        self.assertEqual('file://',
                         ZConfig.loader._url_from_file(MockFile)[:7])

    def test_isPath(self):
        assertTrue = self.assertTrue
        isPath = ZConfig.loader.SchemaLoader().isPath
        assertTrue(isPath("abc"))
        assertTrue(isPath("abc/def"))
        assertTrue(isPath("/abc"))
        assertTrue(isPath("/abc/def"))
        assertTrue(isPath(r"\abc"))
        assertTrue(isPath(r"\abc\def"))
        assertTrue(isPath(r"c:\abc\def"))
        assertTrue(isPath("/ab:cd"))
        assertTrue(isPath(r"\ab:cd"))
        assertTrue(isPath("long name with spaces"))
        assertTrue(isPath("long name:with spaces"))
        assertTrue(not isPath("ab:cd"))
        assertTrue(not isPath("http://www.example.com/"))
        assertTrue(not isPath("http://www.example.com/sample.conf"))
        assertTrue(not isPath("file:///etc/zope/zope.conf"))
        assertTrue(not isPath("file:///c|/foo/bar.conf"))


class TestNonExistentResources(unittest.TestCase):

    # XXX Not sure if this is the best approach for these.  These
    # tests make sure that the error reported by ZConfig for missing
    # resources is handled in a consistent way.  Since ZConfig uses
    # urllib2.urlopen() for opening all resources, what we do is
    # replace that function with one that always raises an exception.
    # Since urllib2.urlopen() can raise either IOError or OSError
    # (depending on the version of Python), we run test for each
    # exception.  urllib2.urlopen() is restored after running the
    # test.

    def setUp(self):
        self.urllib2_urlopen = urllib2.urlopen
        urllib2.urlopen = self.fake_urlopen

    def tearDown(self):
        urllib2.urlopen = self.urllib2_urlopen

    def fake_urlopen(self, url):
        raise self.error()

    def test_nonexistent_file_ioerror(self):
        self.error = IOError
        self.check_nonexistent_file()

    def test_nonexistent_file_oserror(self):
        self.error = OSError
        self.check_nonexistent_file()

    def check_nonexistent_file(self):
        fn = tempfile.mktemp()
        schema = ZConfig.loadSchemaFile(StringIO("<schema/>"))
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadSchema, fn)
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadConfig, schema, fn)
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadConfigFile, schema,
                          StringIO("%include " + fn))
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadSchema,
                          "http://www.zope.org/no-such-document/")
        self.assertRaises(ZConfig.ConfigurationError,
                          ZConfig.loadConfig, schema,
                          "http://www.zope.org/no-such-document/")


class TestResourcesInZip(unittest.TestCase):

    def setUp(self):
        self.old_path = sys.path[:]
        # now add our sample EGG to sys.path:
        zipfile = os.path.join(os.path.dirname(myfile), "foosample.zip")
        sys.path.append(zipfile)

    def tearDown(self):
        sys.path[:] = self.old_path

    def test_zip_import_component_from_schema(self):
        sio = StringIO('''
            <schema>
              <abstracttype name="something"/>
              <import package="foo.sample"/>
              <section name="*"
                       attribute="something"
                       type="something"
                       />
            </schema>
            ''')
        schema = ZConfig.loadSchemaFile(sio)
        t = schema.gettype("sample")
        self.assertFalse(t.isabstract())

    def test_zip_import_component_from_config(self):
        sio = StringIO('''
            <schema>
              <abstracttype name="something"/>
              <section name="*"
                       attribute="something"
                       type="something"
                       />
            </schema>
            ''')
        schema = ZConfig.loadSchemaFile(sio)

        value = '''
            %import foo.sample
            <sample>
              data value
            </sample>
            '''
        sio = StringIO(value)
        config, _ = ZConfig.loadConfigFile(schema, sio)
        self.assertEqual(config.something.data, "| value |")

        sio = StringIO(value)
        with self.assertRaises(ZConfig.ConfigurationSyntaxError):
            ZConfig.loadConfigFile(schema, sio,
                                   overrides=["sample/data=othervalue"])

class TestOpenPackageResource(unittest.TestCase):

    magic_name = 'not a valid import name'

    def setUp(self):
        sys.modules[self.magic_name] = self

    def tearDown(self):
        del sys.modules[self.magic_name]

    def test_package_loader_resource_error(self):
        class MockLoader(object):
            pass
        self.__loader__ = MockLoader()
        self.__path__ = ['dir']

        self.assertRaisesRegexp(ZConfig.SchemaResourceError,
                                "error opening schema component",
                                ZConfig.loader.openPackageResource,
                                self.magic_name, 'a path')

        # Now with an empty path
        self.__path__ = []
        self.assertRaisesRegexp(ZConfig.SchemaResourceError,
                                "schema component not found",
                                ZConfig.loader.openPackageResource,
                                self.magic_name, 'a path')

    def test_resource(self):
        r = ZConfig.loader.Resource(self, None)
        self.assertEqual(self.magic_name, r.magic_name)


def test_suite():
    suite = unittest.makeSuite(LoaderTestCase)
    suite.addTest(unittest.makeSuite(TestNonExistentResources))
    suite.addTest(unittest.makeSuite(TestResourcesInZip))
    suite.addTest(unittest.makeSuite(TestOpenPackageResource))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
