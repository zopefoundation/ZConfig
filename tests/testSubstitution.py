"""Tests of the string interpolation module."""

# This is needed to support Python 2.1.
from __future__ import nested_scopes

import unittest

from ZConfig.Substitution import get, substitute
from ZConfig.Substitution import SubstitutionRecursionError
from ZConfig.Substitution import SubstitutionSyntaxError


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

    def test_undefined_names(self):
        d = {"name": "value"}
        self.assertEqual(substitute("$splat", d), "")
        self.assertEqual(substitute("$splat1", d), "")
        self.assertEqual(substitute("$splat_", d), "")

    def test_syntax_errors(self):
        d = {"name": "value"}
        def check(s):
            self.assertRaises(SubstitutionSyntaxError,
                              substitute, s, d)
        check("${")
        check("${name")
        check("${1name}")
        check("${ name}")

    def test_edge_cases(self):
        # It's debatable what should happen for these cases, so we'll
        # follow the lead of the Bourne shell here.
        def check(s):
            self.assertEqual(substitute(s, {}), s)
        check("$1")
        check("$")
        check("$ stuff")

    def test_non_nesting(self):
        d = {"name": "$value"}
        self.assertEqual(substitute("$name", d), "$value")

    def test_simple_nesting(self):
        d = {"name": "value",
             "nest": "$splat",
             "splat": "nested"}
        def check(name, value):
            self.assertEqual(get(d, name), value)
        check("name", "value")
        check("nest", "nested")

    def test_nesting_errors(self):
        d = {"name": "$splat",
             "splat": "$name"}
        self.assertRaises(SubstitutionRecursionError,
                          get, d, "name")
        d = {"name": "$splat",
             "splat": "$splat"}
        self.assertRaises(SubstitutionRecursionError,
                          get, d, "name")


def test_suite():
    return unittest.makeSuite(SubstitutionTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
