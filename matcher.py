##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""Utility that manages the binding of configuration data to a section."""

import types

import ZConfig

from ZConfig.info import ValueInfo


class BaseMatcher:
    def __init__(self, info, type, handlers):
        self.info = info
        self.type = type
        self._values = [None] * len(type)
        self._sectionnames = {}
        if handlers is None:
            handlers = []
        self._handlers = handlers

    def __repr__(self):
        clsname = self.__class__.__name__
        extra = "type " + `self.type.name`
        return "<%s for %s>" % (clsname, extra)

    def addSection(self, type, name, sectvalue):
        if name:
            if self._sectionnames.has_key(name):
                raise ZConfig.ConfigurationError(
                    "section names must not be re-used within the"
                    " same container:" + `name`)
            self._sectionnames[name] = name
        i = self.type.getsectionindex(type, name)
        ci = self.type.getsectioninfo(type, name)
        v = self._values[i]
        if v is None:
            if ci.ismulti():
                self._values[i] = [sectvalue]
            else:
                self._values[i] = sectvalue
        elif ci.ismulti():
            v.append(sectvalue)
        else:
            raise ZConfig.ConfigurationError(
                "too many instances of %s section" % `ci.sectiontype.name`)

    def addValue(self, key, value, position):
        length = len(self.type)
        arbkey_info = None
        for i in range(length):
            k, ci = self.type[i]
            if k == key:
                break
            if ci.name == "+" and not ci.issection():
                arbkey_info = i, k, ci
        else:
            if arbkey_info is None:
                raise ZConfig.ConfigurationError(
                    `key` + " is not a known key name")
            i, k, ci = arbkey_info
        if ci.issection():
            if ci.name:
                extra = " in %s sections" % `self.type.name`
            else:
                extra = ""
            raise ZConfig.ConfigurationError(
                "%s is not a valid key name%s" % (`key`, extra))

        ismulti = ci.ismulti()
        v = self._values[i]
        if v is None:
            if k == '+':
                v = {}
            elif ismulti:
                v = []
            self._values[i] = v
        elif not ismulti:
            if k != '+':
                raise ZConfig.ConfigurationError(
                    `key` + " does not support multiple values")
        elif len(v) == ci.maxOccurs:
            raise ZConfig.ConfigurationError(
                "too many values for " + `name`)

        value = ValueInfo(value, position)
        if k == '+':
            if ismulti:
                if v.has_key(key):
                    v[key].append(value)
                else:
                    v[key] = [value]
            else:
                if v.has_key(key):
                    raise ZConfig.ConfigurationError(
                        "too many values for " + `key`)
                v[key] = value
        elif ismulti:
            v.append(value)
        else:
            self._values[i] = value

    def finish(self):
        """Check the constraints of the section and convert to an application
        object."""
        length = len(self.type)
        values = self._values
        attrnames = [None] * length
        for i in range(length):
            key, ci = self.type[i]
            attrnames[i] = ci.attribute or key
            v = values[i]
            if v is None and ci.name == '+' and not ci.issection():
                if ci.minOccurs > 0:
                    raise ZConfig.ConfigurationError(
                        "no keys defined for the %s key/value map; at least %d"
                        " must be specified" % (ci.attribute, ci.minOccurs))
                v = {}
                values[i] = v
            if v is None and ci.minOccurs:
                default = ci.getdefault()
                if default is None:
                    if key:
                        s = `key`
                    else:
                        s = "section type " + `ci.sectiontype.name`
                    raise ZConfig.ConfigurationError(
                        "no values for %s; %s required" % (s, ci.minOccurs))
                else:
                    v = values[i] = default[:]
            if ci.ismulti():
                if v is None:
                    v = values[i] = ci.getdefault()[:]
                if len(v) < ci.minOccurs:
                    raise ZConfig.ConfigurationError(
                        "not enough values for %s; %d found, %d required"
                        % (`key`, len(v), ci.minOccurs))
            if v is None and not ci.issection():
                if ci.ismulti():
                    v = ci.getdefault()[:]
                else:
                    v = ci.getdefault()
                values[i] = v
        return self.constuct(attrnames)

    def constuct(self, attrnames):
        values = self._values
        for i in range(len(values)):
            name, ci = self.type[i]
            if ci.ismulti():
                if ci.issection():
                    v = []
                    for s in values[i]:
                        if s is not None:
                            v.append(s._type.datatype(s))
                        else:
                            v.append(None)
                elif ci.name == '+':
                    v = values[i]
                    for key, val in v.items():
                        v[key] = [vi.convert(ci.datatype) for vi in val]
                else:
                    v = [vi.convert(ci.datatype) for vi in values[i]]
            elif ci.issection():
                if values[i] is not None:
                    v = values[i]._type.datatype(values[i])
                else:
                    v = None
            elif name == '+':
                v = values[i]
                for key, val in v.items():
                    v[key] = val.convert(ci.datatype)
            else:
                v = values[i]
                if v is not None:
                    v = v.convert(ci.datatype)
            values[i] = v
            if ci.handler is not None:
                self._handlers.append((ci.handler, v))
        return self.createValue(attrnames)

    def createValue(self, attrnames):
        return SectionValue(attrnames, self._values, None, self.type)


class SectionMatcher(BaseMatcher):
    def __init__(self, info, type, name, handlers):
        if name or info.allowUnnamed():
            self.name = name
        else:
            raise ZConfig.ConfigurationError(
                `type.name` + " sections may not be unnamed")
        BaseMatcher.__init__(self, info, type, handlers)

    def createValue(self, attrnames):
        return SectionValue(attrnames, self._values, self.name, self.type)


class SchemaMatcher(BaseMatcher):
    def __init__(self, info, handlers=None):
        BaseMatcher.__init__(self, info, info, handlers)

    def finish(self):
        # Since there's no outer container to call datatype()
        # for the schema, we convert on the way out.
        v = BaseMatcher.finish(self)
        v = self.type.datatype(v)
        if self.type.handler is not None:
            self._handlers.append((self.type.handler, v))
        return v


class SectionValue:
    """Generic 'bag-of-values' object for a section.

    Derived classes should always call the SectionValue constructor
    before attempting to modify self.
    """

    def __init__(self, attrnames, values, name, type):
        d = self.__dict__
        d['_attrnames'] = attrnames
        d['_values'] = values
        d['_name'] = name
        d['_type'] = type

    def __repr__(self):
        if self._name:
            # probably unique for a given config file; more readable than id()
            name = `self._name`
        else:
            # identify uniquely
            name = "at %#x" % id(self)
        clsname = self.__class__.__name__
        return "<%s for %s %s>" % (clsname, self._type.name, name)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, index):
        if isinstance(index, types.SliceType):
            raise TypeError("SectionValue does not support slicing")
        return self._values[index]

    def __setitem__(self, index, value):
        if isinstance(index, types.SliceType):
            raise TypeError("SectionValue does not support slicing")
        self._values[index] = value

    def __getattr__(self, name):
        try:
            i = self._attrnames.index(name)
        except ValueError:
            raise AttributeError, name
        return self._values[i]

    def __setattr__(self, name, value):
        try:
            i = self._attrnames.index(name)
        except ValueError:
            self.__dict__[name] = value
        else:
            self._values[i] = value

    def __str__(self):
        l = []
        for i in range(len(self._attrnames)):
            k = self._attrnames[i]
            v = self._values[i]
            l.append('%-40s: %s' % (k, v))
        return '\n'.join(l)

    def getSectionName(self):
        return self._name

    def getSectionType(self):
        return self._type.name
