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
"""Parser for ZConfig schemas."""

import xml.sax
import xml.sax.saxutils

import ZConfig

from ZConfig import info
from ZConfig import url


try:
    True
except NameError:
    True = 1
    False = 0

try:
    dict
except NameError:
    def dict(mapping):
        d = {}
        for k, v in mapping.items():
            d[k] = v
        return d


def parseResource(resource, registry, loader):
    parser = SchemaParser(registry, loader, resource.url)
    xml.sax.parse(resource.file, parser)
    return parser._schema


class SchemaParser(xml.sax.ContentHandler):

    _cdata_tags = "description", "metadefault", "example", "default"
    _handled_tags = ("schema", "import", "sectiongroup", "sectiontype",
                     "key", "multikey", "section", "multisection")

    def __init__(self, registry, loader, url):
        self._registry = registry
        self._loader = loader
        self._basic_key = registry.get("basic-key")
        self._identifier = registry.get("identifier")
        self._cdata = None
        self._locator = None
        self._prefixes = []
        self._schema = None
        self._stack = []
        self._group = None
        self._url = url

    # SAX 2 ContentHandler methods

    def setDocumentLocator(self, locator):
        self._locator = locator

    def startElement(self, name, attrs):
        attrs = dict(attrs)
        if name == "schema":
            if self._schema is not None:
                self.error("schema element improperly nested")
            self.start_schema(attrs)
        elif name in self._handled_tags:
            if self._schema is None:
                self.error(name + " element outside of schema")
            getattr(self, "start_" + name)(attrs)
        elif name in self._cdata_tags:
            if self._schema is None:
                self.error(name + " element outside of schema")
            if self._cdata is not None:
                self.error(name + " element improperly nested")
            self._cdata = []
            self._position = None
        else:
            self.error("Unknown tag " + name)

    def characters(self, data):
        if self._cdata is not None:
            if self._position is None:
                self._position = self.get_position()
            self._cdata.append(data)
        elif data.strip():
            self.error("unexpected non-blank character data: "
                       + `data.strip()`)

    def endElement(self, name):
        if name in self._handled_tags:
            getattr(self, "end_" + name)()
        else:
            data = ''.join(self._cdata).strip()
            self._cdata = None
            if name == "default":
                # value for a key
                self._stack[-1].adddefault(data, self._position)
            else:
                setattr(self._stack[-1], name, data)

    def endDocument(self):
        if self._schema is None:
            self.error("no schema found")

    # schema loading logic

    def start_import(self, attrs):
        src = attrs.get("src", "").strip()
        pkg = attrs.get("package", "").strip()
        if not (src or pkg):
            self.error("import must specify either src or package")
        if src and pkg:
            self.error("import may only specify one of src or package")
        if src:
            src = url.urljoin(self._url, src)
            src, fragment = url.urldefrag(src)
            if fragment:
                self.error("import src many not include a fragment identifier")
            urls = [src]
        else:
            raise NotImpementedError(
                "<import package='...'/> not yet implemented")
        for s in urls:
            schema = self._loader.loadURL(s)
            for n in schema.gettypenames():
                self._schema.addtype(schema.gettype(n))

    def end_import(self):
        pass

    def get_position(self):
        if self._locator:
            return (self._locator.getLineNumber(),
                    self._locator.getColumnNumber(),
                    self._url)
        else:
            return None, None, self._url

    def get_handler(self, attrs):
        v = attrs.get("handler")
        if v is None:
            return v
        else:
            return self.basic_key(v)

    def push_prefix(self, attrs):
        name = attrs.get("prefix")
        if name:
            if name.startswith(".") and self._prefixes:
                prefix = self._prefixes[-1] + name
            elif name.startswith("."):
                self.error("prefix may not begin with '.'")
            else:
                prefix = name
        elif self._prefixes:
            prefix = self._prefixes[-1]
        else:
            prefix = ''
        self._prefixes.append(prefix)

    def get_classname(self, name):
        if name.startswith("."):
            return self._prefixes[-1] + name
        else:
            return name

    def get_datatype(self, attrs, attrkey, default):
        if attrs.has_key(attrkey):
            dtname = self.get_classname(attrs[attrkey])
        else:
            dtname = default

        try:
            return self._registry.get(dtname)
        except ValueError, e:
            self.error(e[0])

    def get_sect_typeinfo(self, attrs):
        keytype = self.get_datatype(attrs, "keytype", "basic-key")
        valuetype = self.get_datatype(attrs, "valuetype", "string")
        datatype = self.get_datatype(attrs, "datatype", "null")
        return keytype, valuetype, datatype

    def start_schema(self, attrs):
        self.push_prefix(attrs)
        handler = self.get_handler(attrs)
        keytype, valuetype, datatype = self.get_sect_typeinfo(attrs)
        name = attrs.get("type")
        if name is not None:
            name = self.basic_key(name)
        self._schema = info.SchemaType(name, keytype, valuetype, datatype,
                                       handler, self._url, self._registry)
        if name is not None:
            # XXX circular reference
            self._schema.addtype(self._schema)
        self._stack = [self._schema]

    def end_schema(self):
        del self._prefixes[-1]
        assert not self._prefixes

    def start_sectiontype(self, attrs):
        name = attrs.get("type")
        if not name:
            self.error("sectiontype type must not be omitted or empty")
        name = self.basic_key(name)
        self.push_prefix(attrs)
        keytype, valuetype, datatype = self.get_sect_typeinfo(attrs)
        if attrs.has_key("extends"):
            basename = self.basic_key(attrs["extends"])
            if basename == name:
                self.error("sectiontype cannot extend itself")
            base = self._schema.gettype(basename)
            if base.istypegroup():
                self.error("sectiontype cannot extend an abstract type")
            if attrs.has_key("keytype"):
                self.error("derived sectiontype may not specify a keytype")
            sectinfo = self._schema.deriveSectionType(
                base, name, valuetype, datatype)
        else:
            sectinfo = self._schema.createSectionType(
                name, keytype, valuetype, datatype)
        if self._group is not None:
            if attrs.has_key("group"):
                self.error("sectiontype cannot specify group"
                           " if nested in a sectiongroup")
            self._group.addsubtype(sectinfo)
        elif attrs.has_key("group"):
            groupname = self.basic_key(attrs["group"])
            group = self._schema.gettype(groupname)
            if not group.istypegroup():
                self.error("type specified as group is not a sectiongroup")
            group.addsubtype(sectinfo)
        self._stack.append(sectinfo)

    def end_sectiontype(self):
        del self._prefixes[-1]
        self._stack.pop()

    def get_required(self, attrs):
        if attrs.has_key("required"):
            v = attrs["required"]
            if v == "yes":
                return True
            elif v == "no":
                return False
            self.error("value for 'required' must be 'yes' or 'no'")
        else:
            return False

    def get_ordinality(self, attrs):
        min, max = 0, info.Unbounded
        if self.get_required(attrs):
            min = 1
        return min, max

    def get_sectiontype(self, attrs):
        type = attrs.get("type")
        if not type:
            self.error("section must specify type")
        return self._schema.gettype(type)

    def start_section(self, attrs):
        sectiontype = self.get_sectiontype(attrs)
        handler = self.get_handler(attrs)
        min = self.get_required(attrs) and 1 or 0
        any, name, attribute = self.get_name_info(attrs, "section")
        if any and not attribute:
            self.error(
                "attribute must be specified if section name is '*' or '+'")
        section = info.SectionInfo(any or name, sectiontype,
                                   min, 1, handler, attribute)
        self._stack[-1].addsection(name, section)
        self._stack.append(section)

    def end_section(self):
        self._stack.pop()

    def start_multisection(self, attrs):
        sectiontype = self.get_sectiontype(attrs)
        min, max = self.get_ordinality(attrs)
        any, name, attribute = self.get_name_info(attrs, "multisection")
        if any not in ("*", "+"):
            self.error("multisection must specify '*' or '+' for the name")
        handler = self.get_handler(attrs)
        section = info.SectionInfo(any or name, sectiontype,
                                   min, max, handler, attribute)
        self._stack[-1].addsection(name, section)
        self._stack.append(section)

    def end_multisection(self):
        self._stack.pop()

    def start_sectiongroup(self, attrs):
        if self._group is not None:
            self.error("sectiongroup elements cannot be nested")
        self.push_prefix(attrs)
        name = attrs.get("type")
        if not name:
            self.error("sectiongroup must be named")
        name = self.basic_key(name)
        self._group = info.GroupType(name)
        self._schema.addtype(self._group)
        self._stack.append(self._group)

    def end_sectiongroup(self):
        del self._prefixes[-1]
        self._group = None
        self._stack.pop()

    def get_key_info(self, attrs, element):
        any, name, attribute = self.get_name_info(attrs, element)
        if any == '*':
            self.error(element + " may not specify '*' for name")
        if not name and any != '+':
            self.error(element + " name may not be omitted or empty")
        datatype = self.get_datatype(attrs, "datatype", "string")
        handler = self.get_handler(attrs)
        return name or any, datatype, handler, attribute

    def start_key(self, attrs):
        name, datatype, handler, attribute = self.get_key_info(attrs, "key")
        min = self.get_required(attrs) and 1 or 0
        key = info.KeyInfo(name, datatype, min, 1, handler, attribute)
        if attrs.has_key("default"):
            if min:
                self.error("required key cannot have a default value")
            key.adddefault(str(attrs["default"]).strip(),
                           self.get_position())
        key.finish()
        self._stack[-1].addkey(key)
        self._stack.append(key)

    def end_key(self):
        self._stack.pop()

    def start_multikey(self, attrs):
        if attrs.has_key("default"):
            self.error("default values for multikey must be given using"
                       " 'default' elements")
        name, datatype, handler, attribute = self.get_key_info(attrs,
                                                               "multikey")
        min, max = self.get_ordinality(attrs)
        key = info.KeyInfo(name, datatype, min, max, handler, attribute)
        self._stack[-1].addkey(key)
        self._stack.append(key)

    def end_multikey(self):
        self._stack.pop().finish()

    def get_name_info(self, attrs, element):
        name = attrs.get("name")
        if not name:
            self.error(element + " name must be specified and non-empty")
        aname = attrs.get("attribute")
        if aname:
            aname = self.identifier(aname)
            if aname.startswith("getSection"):
                # reserved; used for SectionValue methods to get meta-info
                self.error("attribute names may not start with 'getSection'")
        if name in ("*", "+"):
            if not aname:
                self.error(
                    "container attribute must be specified and non-empty"
                    " when using '*' or '+' for a section name")
            return name, None, aname
        else:
            # run the keytype converter to make sure this is a valid key
            name = self._stack[-1].keytype(name)
            if not aname:
                aname = self.basic_key(name)
                aname = self.identifier(aname.replace('-', '_'))
            return None, self.basic_key(name), aname

    # datatype conversion wrappers

    def basic_key(self, s):
        try:
            return self._basic_key(s)
        except ValueError, e:
            self.error(e[0])
        except ZConfig.SchemaError, e:
            self.initerror(e)
            raise

    def identifier(self, s):
        try:
            return self._identifier(s)
        except ValueError, e:
            self.error(e[0])
        except ZConfig.SchemaError, e:
            self.initerror(e)
            raise

    # exception setup helpers

    def initerror(self, e):
        if self._locator is not None:
            e.colno = self._locator.getColumnNumber()
            e.lineno = self._locator.getLineNumber()
            e.url = self._locator.getSystemId()
        return e

    def error(self, message):
        raise self.initerror(ZConfig.SchemaError(message))
