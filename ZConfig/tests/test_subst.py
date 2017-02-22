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
"""Tests of the string interpolation module."""

# This is needed to support Python 2.1.
from __future__ import nested_scopes
import os

import unittest

from ZConfig import SubstitutionReplacementError, SubstitutionSyntaxError
from ZConfig.substitution import isname, substitute


class SubstitutionTestCase(unittest.TestCase):
    def test_simple_names(self):
        d = {"name": "value",
             "name1": "abc",
             "name_": "def",
             "_123": "ghi"}
        def check(s, v):
            self.assertEqual(substitute(s, d), v)
        check("$name", "value")
        check(" $name ", " value ")
        check("${name}", "value")
        check(" ${name} ", " value ")
        check("$name$name", "valuevalue")
        check("$name1$name", "abcvalue")
        check("$name_$name", "defvalue")
        check("$_123$name", "ghivalue")
        check("$name $name", "value value")
        check("$name1 $name", "abc value")
        check("$name_ $name", "def value")
        check("$_123 $name", "ghi value")
        check("splat", "splat")
        check("$$", "$")
        check("$$$name$$", "$value$")

        # Check for an ENV var
        self.assertEqual(substitute("$(PATH)", d), os.getenv("PATH"))

    def test_undefined_names(self):
        d = {"name": "value"}
        self.assertRaises(SubstitutionReplacementError,
                          substitute, "$splat", d)
        self.assertRaises(SubstitutionReplacementError,
                          substitute, "$splat1", d)
        self.assertRaises(SubstitutionReplacementError,
                          substitute, "$splat_", d)

        # An undefined ENV should also rise
        self.assertRaises(SubstitutionReplacementError,
                          substitute, "$(MY_SUPER_PATH)", d)

    def test_syntax_errors(self):
        d = {"name": "${next"}
        def check(s):
            self.assertRaises(SubstitutionSyntaxError,
                              substitute, s, d)
        check("${")
        check("${name")
        check("${1name}")
        check("${ name}")
        check("$(")
        check("$(name")
        check("$(1name)")
        check("$( name)")

    def test_edge_cases(self):
        # It's debatable what should happen for these cases, so we'll
        # follow the lead of the Bourne shell here.
        def check(s):
            self.assertRaises(SubstitutionSyntaxError,
                              substitute, s, {})
        check("$1")
        check("$")
        check("$ stuff")

    def test_non_nesting(self):
        d = {"name": "$value"}
        self.assertEqual(substitute("$name", d), "$value")

    def test_isname(self):
        self.assertTrue(isname("abc"))
        self.assertTrue(isname("abc_def"))
        self.assertTrue(isname("_abc"))
        self.assertTrue(isname("abc_"))
        self.assertTrue(not isname("abc-def"))
        self.assertTrue(not isname("-def"))
        self.assertTrue(not isname("abc-"))
        self.assertTrue(not isname(""))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
