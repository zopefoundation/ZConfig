##############################################################################
#
# Copyright (c) 2017 Zope Foundation and Contributors.
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
from __future__ import absolute_import

import unittest

from ZConfig import validator

from .support import input_file
from .support import with_stdin_from_input_file

def run_validator(*args):
    return validator.main(args)

class TestValidator(unittest.TestCase):

    def test_no_schema(self):
        self.assertRaises(SystemExit,
                          run_validator)

    def test_schema_only(self):
        res = run_validator("--schema", input_file('simple.xml'))
        self.assertEqual(res, 0)

    @with_stdin_from_input_file('simple.conf')
    def test_schema_only_redirect(self):
        res = run_validator("--schema", input_file('simple.xml'))
        self.assertEqual(res, 0)

    def test_good_config(self):
        res = run_validator("--schema", input_file('simple.xml'),
                            input_file('simple.conf'),
                            input_file('simple.conf'))
        self.assertEqual(res, 0)

    def test_bad_config(self):
        res = run_validator("--schema", input_file("simple.xml"),
                            input_file("outer.conf"))
        self.assertEqual(res, 1)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
