"""Tests of the string interpolation module."""

import unittest

from ZConfig.Interpolation import get, interpolate
from ZConfig.Interpolation import InterpolationRecursionError
from ZConfig.Interpolation import InterpolationSyntaxError


class InterpolationTestCase(unittest.TestCase):
    def test_simple_names(self):
        d = {"name": "value",
             "name1": "abc",
             "name_": "def",
             "_123": "ghi"}
        def check(s, v):
            self.assertEqual(interpolate(s, d), v)
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
        self.assertEqual(interpolate("$splat", d), "")
        self.assertEqual(interpolate("$splat1", d), "")
        self.assertEqual(interpolate("$splat_", d), "")

    def test_syntax_errors(self):
        d = {"name": "value"}
        def check(s):
            self.assertRaises(InterpolationSyntaxError,
                              interpolate, s, d)
        check("$1")
        check("${")
        check("${name")
        check("${1name}")
        check("${ name}")

    def test_edge_cases(self):
        # It's debatable what should happen for these cases, so we'll
        # follow the lead of the Bourne shell here.
        def check(s, value):
            self.assertEqual(interpolate(s, {}), value)
        check("$", "$")
        check("$ stuff", "$ stuff")

    def test_non_nesting(self):
        d = {"name": "$value"}
        self.assertEqual(interpolate("$name", d), "$value")

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
             "splat": "$foo",
             "foo": "$"}
        self.assertRaises(InterpolationSyntaxError,
                          get, d, "name")
        d = {"name": "$splat",
             "splat": "$name"}
        self.assertRaises(InterpolationRecursionError,
                          get, d, "name")
        d = {"name": "$splat",
             "splat": "$splat"}
        self.assertRaises(InterpolationRecursionError,
                          get, d, "name")


def test_suite():
    return unittest.makeSuite(InterpolationTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
