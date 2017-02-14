##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""\
Test driver for ZConfig.schemaless.

"""
__docformat__ = "reStructuredText"

import doctest
import unittest

from ZConfig.schemaless import Section

class TestSection(unittest.TestCase):

    def test_init_with_data(self):
        s = Section(data={'k': 'v'})
        self.assertDictEqual(s, {'k': 'v'})

def test_suite():
    suite = unittest.makeSuite(TestSection)
    suite.addTest(doctest.DocFileSuite("schemaless.txt", package="ZConfig"))
    return suite
