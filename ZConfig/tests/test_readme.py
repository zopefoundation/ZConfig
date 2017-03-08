##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
import doctest
import os
import os.path
import unittest
import logging


options = doctest.REPORT_NDIFF | doctest.ELLIPSIS

old = {}
def setUp(test):
    logger = logging.getLogger()
    old['level'] = logger.level
    old['handlers'] = logger.handlers[:]

def tearDown(test):
    logger = logging.getLogger()
    logger.level = old['level']
    logger.handlers = old['handlers']

def docSetUp(test):
    old['pwd'] = os.getcwd()
    doc_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..',
        '..',
        'doc')
    os.chdir(doc_path)
    setUp(test)

def docTearDown(test):
    os.chdir(old['pwd'])
    tearDown(test)

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            '../../README.rst',
            optionflags=options,
            setUp=setUp, tearDown=tearDown,
        ),
        doctest.DocFileSuite(
            '../../doc/using-logging.rst',
            optionflags=options, globs=globals(),
            setUp=docSetUp, tearDown=docTearDown,
        ),
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
