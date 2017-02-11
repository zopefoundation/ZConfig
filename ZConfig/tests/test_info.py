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

from ZConfig import SchemaError
from ZConfig import ConfigurationError

from ZConfig.info import Unbounded
from ZConfig.info import BaseInfo
from ZConfig.info import BaseKeyInfo
from ZConfig.info import KeyInfo
from ZConfig.info import SectionInfo
from ZConfig.info import AbstractType
from ZConfig.info import SectionType
from ZConfig.info import SchemaType

class UnboundTestCase(unittest.TestCase):

    def test_order(self):
        self.assertGreater(Unbounded, self)
        self.assertFalse(Unbounded > Unbounded)
        self.assertEqual(Unbounded, Unbounded)

class InfoMixin(object):

    Class = None

    default_kwargs = {'name': '', 'datatype': None, 'handler': None,
                      'minOccurs': None, 'maxOccurs': None, 'attribute': None}

    def make_one(self, **kwargs):
        args = self.default_kwargs.copy()
        args.update(kwargs)
        return self.Class(**args)


class BaseInfoTestCase(InfoMixin, unittest.TestCase):

    Class = BaseInfo

    def test_constructor_error(self):
        self.assertRaisesRegexp(SchemaError,
                                'maxOccurs',
                                self.make_one,
                                maxOccurs=0)

        # This case doesn't really make sense
        self.assertRaisesRegexp(SchemaError,
                                'minOccurs',
                                self.make_one,
                                maxOccurs=1,
                                minOccurs=2)

    def test_repr(self):
        # just doesn't raise
        repr(self.make_one())

class BaseKeyInfoTestCase(InfoMixin, unittest.TestCase):

    class Class(BaseKeyInfo):
        def add_valueinfo(self, vi, key):
            "This wont actually be called"

    def test_cant_instantiate(self):
        self.Class = BaseKeyInfo
        with self.assertRaises(TypeError):
            self.make_one()
        del self.Class

    def test_finish(self):
        info = self.make_one(minOccurs=1)
        info.finish()
        with self.assertRaises(SchemaError):
            info.finish()

    def test_adddefaultc(self):
        info = self.make_one(name='foo', minOccurs=1)
        self.assertRaisesRegexp(SchemaError,
                                'unexpected key for default',
                                info.adddefault,
                                None, None, key='key')

class KeyInfoTestCase(InfoMixin, unittest.TestCase):

    Class = KeyInfo
    default_kwargs = InfoMixin.default_kwargs.copy()
    default_kwargs.pop('maxOccurs')

    def test_add_with_default(self):
        info = self.make_one(minOccurs=1, name='name')
        info.adddefault('value', None)
        self.assertRaisesRegexp(SchemaError,
                                'cannot set more than one',
                                info.adddefault,
                                'value', None)

class SectionInfoTestCase(InfoMixin, unittest.TestCase):

    Class = SectionInfo

    class MockSectionType(object):
        name = None
        @classmethod
        def isabstract(cls):
            return True

    default_kwargs = InfoMixin.default_kwargs.copy()
    default_kwargs.pop('datatype')
    default_kwargs['sectiontype'] = MockSectionType

    def test_constructor_error(self):
        self.assertRaisesRegexp(SchemaError,
                                'must use a name',
                                self.make_one,
                                name='name', maxOccurs=2)
        self.assertRaisesRegexp(SchemaError,
                                'must specify a target attribute',
                                self.make_one,
                                name='*', maxOccurs=2)

    def test_misc(self):
        info = self.make_one(maxOccurs=1)
        repr(info)
        self.assertFalse(info.isAllowedName('*'))
        self.assertFalse(info.isAllowedName('+'))

class AbstractTypeTestCase(unittest.TestCase):

    def test_subtypes(self):

        t = AbstractType('name')
        self.assertFalse(t.hassubtype('foo'))
        self.assertEqual([], list(t.getsubtypenames()))

        self.name = 'foo'
        t.addsubtype(self)
        self.assertTrue(t.hassubtype('foo'))

class SectionTypeTestCase(unittest.TestCase):

    def make_one(self, name='', keytype=None, valuetype=None,
                 datatype=None, registry={}, types=None):
        return SectionType(name, keytype, valuetype, datatype, registry, types)

    def test_getinfo_no_key(self):
        info = self.make_one()
        self.assertRaisesRegexp(ConfigurationError,
                                "cannot match a key without a name",
                                info.getinfo,
                                None)

    def test_required_types_with_name(self):
        info = self.make_one(name='foo')
        self.assertEqual(['foo'], info.getrequiredtypes())

    def test_getsectioninfo(self):
        class MockChild(object):
            _issection = False
            def issection(self):
                return self._issection
        child = MockChild()

        info = self.make_one()

        info._children.append(('foo', child))

        self.assertRaisesRegexp(ConfigurationError,
                                'already in use for key',
                                info.getsectioninfo,
                                None, 'foo')

        self.assertRaisesRegexp(ConfigurationError,
                                'no matching section',
                                info.getsectioninfo,
                                None, 'baz')

class SchemaTypeTestCase(unittest.TestCase):

    def test_various(self):
        class Mock(object):
            pass

        mock = Mock()
        schema = SchemaType(None, None, None, None, 'url', {})

        mock.name = 'name'
        schema.addtype(mock)
        with self.assertRaises(SchemaError):
            schema.addtype(mock)

        self.assertTrue(schema.allowUnnamed())
        self.assertFalse(schema.isAllowedName(None))

        with self.assertRaises(SchemaError):
            schema.deriveSectionType(schema, None, None, None, None)

        schema.addComponent('name')
        self.assertRaisesRegexp(SchemaError,
                                'already have component',
                                schema.addComponent,
                                'name')

def test_suite():
    suite = unittest.makeSuite(UnboundTestCase)
    suite.addTest(unittest.makeSuite(BaseInfoTestCase))
    suite.addTest(unittest.makeSuite(BaseKeyInfoTestCase))
    suite.addTest(unittest.makeSuite(KeyInfoTestCase))
    suite.addTest(unittest.makeSuite(SectionInfoTestCase))
    suite.addTest(unittest.makeSuite(AbstractTypeTestCase))
    suite.addTest(unittest.makeSuite(SectionTypeTestCase))
    suite.addTest(unittest.makeSuite(SchemaTypeTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
