"""Tests of the string interpolation module."""

# This is needed to support Python 2.1.
from __future__ import nested_scopes

import unittest

from types import StringType
from UserDict import UserDict

from ZConfig.Substitution import get, getnames, substitute
from ZConfig.Substitution import SubstitutionRecursionError
from ZConfig.Substitution import SubstitutionSyntaxError


class ContainerDict(UserDict):
    def __init__(self, mapping=None, container=None):
        self.container = container
        UserDict.__init__(self, mapping)


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
        d = {"name": "${next"}
        def check(s):
            self.check_error_context(SubstitutionSyntaxError, None,
                                     substitute, s, d)
        check("${")
        check("${name")
        check("${1name}")
        check("${ name}")

        self.check_error_context(SubstitutionSyntaxError, ["name"],
                                 get, d, "name")

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
        self.check_error_context(SubstitutionRecursionError, ["name", "splat"],
                                 get, d, "name")
        d = {"name": "$splat",
             "splat": "$splat"}
        self.check_error_context(SubstitutionRecursionError, ["name", "splat"],
                                 get, d, "name")

    def test_container_search(self):
        d1 = {"outer": "outervalue",
              "inner": "inner-from-outer"}
        d2 = ContainerDict({"inner": "inner-from-inner",
                            "bogus": "${nothere}",
                            "both": "${inner} ${outer}"}, d1)
        self.assertEqual(get(d2, "both"),
                         "inner-from-inner outervalue")
        self.assertEqual(get(d2, "bogus"), "")

    def check_error_context(self, exc, context, callable, *args, **kw):
        try:
            callable(*args, **kw)
        except exc, e:
            self.assertEqual(e.context, context)
        else:
            if isinstance(exc, StringType):
                name = `exc`
            elif exc.module == "exceptions":
                # Built-in exceptions
                name = exc.__name__
            else:
                name = exc.__module__ + "." + exc.__name__
            self.fail("expected exception " + name)

    def test_getnames(self):
        self.assertEqual(getnames(""), [])
        self.assertEqual(getnames("abc"), [])
        self.assertEqual(getnames("$"), [])
        self.assertEqual(getnames("$$"), [])
        self.assertEqual(getnames("$abc"), ["abc"])
        self.assertEqual(getnames("$abc$abc"), ["abc"])
        self.assertEqual(getnames("$abc$def"), ["abc", "def"])
        self.assertEqual(getnames("${abc}${def}"), ["abc", "def"])
        self.assertEqual(getnames("$abc xyz${def}pqr$def"), ["abc", "def"])
        self.assertEqual(getnames("$ABC xyz${def}pqr$DEF"), ["abc", "def"])
        self.assertRaises(SubstitutionSyntaxError, getnames, "${")
        self.assertRaises(SubstitutionSyntaxError, getnames, "${name")
        self.assertRaises(SubstitutionSyntaxError, getnames, "${1name}")
        self.assertRaises(SubstitutionSyntaxError, getnames, "${ name}")


def test_suite():
    return unittest.makeSuite(SubstitutionTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
