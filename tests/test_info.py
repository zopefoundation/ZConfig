##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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

"""Tests some ZConfig-internal APIs defined by the ZConfig.info module.

This helps avoid regressions, but is also useful while developing the
helpers to make sure the edge cases are handled properly.
"""

import StringIO
import unittest

import ZConfig


class SectionTypeTests(unittest.TestCase):

    def load_schema_text(self, text):
        sio = StringIO.StringIO(text)
        return ZConfig.loadSchemaFile(
            sio, "<%s.load_schema_text>" % self.__class__.__name__)

    def test_getinfobyname(self):
        schema = self.load_schema_text("""\
            <schema>
              <sectiontype name='st'/>
              <key name='mykey'/>
              <section name='foo' type='st'/>
              <section name='bar' type='st'/>
              <section name='+' type='st' attribute='things'/>
            </schema>
            """)
        info = schema.getinfobyname("mykey")
        self.assertEqual(info.name, "mykey")
        self.assert_(not info.issection())
        info1 = schema.getinfobyname("foo")
        info2 = schema.getinfobyname("bar")
        self.assertEqual(info1.name, "foo")
        self.assert_(info1.issection())
        self.assertEqual(info2.name, "bar")
        self.assert_(info2.issection())
        self.assertEqual(schema.getinfobyname("not-there"), None)
        self.assertRaises(ZConfig.ConfigurationError,
                          schema.getinfobyname, "*")
        self.assertRaises(ZConfig.ConfigurationError,
                          schema.getinfobyname, "+")

    def test_getsectionbytype(self):
        schema = self.load_schema_text("""\
            <schema>
              <sectiontype name='st'/>
              <sectiontype name='st2'/>
              <sectiontype name='st3'/>
              <section name='foo' type='st'/>
              <section name='bar' type='st'/>
              <section name='+' type='st' attribute='things'/>
              <section name='*' type='st3' attribute='splat'/>
            </schema>
            """)
        info = schema.getsectionbytype("st3")
        self.assert_(info.allowUnnamed())
        self.assertEqual(info.sectiontype.name, "st3")
        # defined but not used
        self.assertRaises(ZConfig.ConfigurationError,
                          schema.getsectionbytype, "st2")
        # not defined
        self.assertRaises(ZConfig.ConfigurationError,
                          schema.getsectionbytype, "not-defined")
        # defined and used, but ambiguous
        self.assertRaises(ZConfig.ConfigurationError,
                          schema.getsectionbytype, "st")


def test_suite():
    return unittest.makeSuite(SectionTypeTests)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
