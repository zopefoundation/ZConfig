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

import unittest

from ZConfig import ConfigurationError
from ZConfig import DataConversionError

from ZConfig.matcher import SectionValue
from ZConfig.matcher import SectionMatcher
from ZConfig.matcher import BaseMatcher

class SectionValueTestCase(unittest.TestCase):

    def test_repr(self):
        class MockMatcher(object):
            type = None

        matcher = MockMatcher()
        matcher.type = MockMatcher()
        matcher.type.name = 'matcher'

        sv = SectionValue({}, 'name', matcher)
        self.assertIn('name', repr(sv))

        sv = SectionValue({}, None, matcher)
        self.assertIn('at', repr(sv))

        self.assertIs(matcher, sv.getSectionMatcher())

    def test_str(self):
        d = {'k': 'v'}
        sv = SectionValue(d, None, None)
        self.assertEqual(
            'k                                       : v',
            str(sv))

class SectionMatcherTestCase(unittest.TestCase):

    def test_constructor_error(self):
        class Mock(object):
            name = 'name'
            def allowUnnamed(self):
                return False
        mock = Mock()
        self.assertRaisesRegexp(ConfigurationError,
                                "sections may not be unnamed",
                                SectionMatcher,
                                mock, mock, None, None)

class BaseMatcherTestCase(unittest.TestCase):

    def test_repr(self):
        class Mock(dict):
            name = 'name'

        matcher = BaseMatcher(None, Mock(), None)
        repr(matcher)

    def test_duplicate_section_names(self):
        class Mock(dict):
            name = 'name'

        matcher = BaseMatcher(None, Mock(), None)
        matcher._sectionnames['foo'] = None

        self.assertRaisesRegexp(ConfigurationError,
                                "section names must not be re-used",
                                matcher.addSection,
                                None, 'foo', None)

    def test_construct_errors(self):
        class MockType(object):
            attribute = 'attr'

            _multi = True
            _section = True

            def ismulti(self):
                return self._multi

            def issection(self):
                return self._section

        type_ = []
        matcher = BaseMatcher(None, type_, None)
        type_.append( ('key', MockType() ) )

        class MockSection(object):
            def getSectionDefinition(self):
                return self

            def datatype(self, _s):
                raise ValueError()

        matcher._values['attr'] = [MockSection()]

        with self.assertRaises(DataConversionError):
            matcher.constuct()

        type_[0][1]._multi = False
        matcher._values['attr'] = MockSection()
        with self.assertRaises(DataConversionError):
            matcher.constuct()


    def test_create_child_bad_name(self):

        class MockType(list):
            name = 'foo'
            sectiontype = None

            def getsectioninfo(self, type_name, name):
                return self

            def isabstract(self):
                return False

            def isAllowedName(self, name):
                return False

        t = MockType()
        t.sectiontype = MockType()
        matcher = BaseMatcher(None, t, None)
        self.assertRaisesRegexp(ConfigurationError,
                                'is not an allowed name',
                                matcher.createChildMatcher,
                                MockType(), 'ignored')



def test_suite():
    suite = unittest.makeSuite(SectionValueTestCase)
    suite.addTest(unittest.makeSuite(SectionMatcherTestCase))
    suite.addTest(unittest.makeSuite(BaseMatcherTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
