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
"""Schema loader utility."""

import os.path
import sys
import urllib
import urllib2

import ZConfig

from ZConfig import datatypes
from ZConfig import matcher
from ZConfig.url import urlnormalize, urldefrag, urljoin, urlsplit, urlunsplit

try:
    True
except NameError:
    True = 1
    False = 0


LIBRARY_DIR = os.path.join(sys.prefix, "lib", "zconfig")

RESOURCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "resources")


def loadSchema(url):
    return SchemaLoader().loadURL(url)

def loadSchemaFile(file, url=None):
    return SchemaLoader().loadFile(file, url)

def loadConfig(schema, url):
    return ConfigLoader(schema).loadURL(url)

def loadConfigFile(schema, file, url=None):
    return ConfigLoader(schema).loadFile(file, url)


class BaseLoader:
    def __init__(self):
        pass

    def createResource(self, file, url, fragment=None):
        return Resource(file, url, fragment)

    def loadURL(self, url):
        url = self.normalizeURL(url)
        r = self.openResource(url)
        try:
            return self.loadResource(r)
        finally:
            r.close()

    def loadFile(self, file, url=None):
        if not url:
            url = _url_from_file(file)
        r = self.createResource(file, url)
        return self.loadResource(r)

    # utilities

    def loadResource(self, resource):
        raise NotImpementedError(
            "BaseLoader.loadResource() must be overridden by a subclass")

    def openResource(self, url):
        # XXX This should be replaced to use a local cache for remote
        # resources.  The policy needs to support both re-retrieve on
        # change and provide the cached resource when the remote
        # resource is not accessible.
        url = str(url)
        parts = urlsplit(url)
        fragment = parts[-1]
        if fragment:
            parts = list(parts)
            parts[-1] = ''
            url = urlunsplit(tuple(parts))
        file = urllib2.urlopen(url)
        return self.createResource(file, url, fragment or None)

    def normalizeURL(self, url):
        if os.path.exists(url):
            url = "file://" + urllib.pathname2url(os.path.abspath(url))
        else:
            url = urlnormalize(url)
        if url and not self.allowFragments():
            url, fragment = urldefrag(url)
            if fragment:
                raise ZConfig.ConfigurationError(
                    "fragment identifiers are not supported")
        return url

    def allowFragments(self):
        return False


def _url_from_file(file):
    name = getattr(file, "name", None)
    if name and name[0] != "<" and name[-1] != ">":
        return "file://" + urllib.pathname2url(os.path.abspath(name))
    else:
        return None


class SchemaLoader(BaseLoader):
    def __init__(self, registry=None, library=None):
        if registry is None:
            registry = datatypes.Registry()
        BaseLoader.__init__(self)
        self.registry = registry
        self._cache = {}
        if library is None:
            library = LIBRARY_DIR
        self._library = library

    def loadResource(self, resource):
        if resource.url and self._cache.has_key(resource.url):
            schema = self._cache[resource.url]
        else:
            from ZConfig.schema import parseResource
            schema = parseResource(resource, self.registry, self)
            self._cache[resource.url] = schema
        if resource.fragment:
            type = self.registry.get("basic-key")(resource.fragment)
            schema = schema.gettype(type)
        return schema

    def allowFragments(self):
        return True

    # schema parser support API

    def schemaPackageURLs(self, package):
        parts = package.split(".")
        if not parts:
            raise ZConfig.SchemaError(
                "illegal schema component name: " + `package`)
        if len(filter(None, parts)) != len(parts):
            # '' somewhere in the package spec; still illegal
            raise ZConfig.SchemaError(
                "illegal schema component name: " + `package`)
        dirname = os.path.join(self._library, *parts)
        fn = os.path.join(dirname, "schema.xml")
        if not os.path.exists(fn):
            raise ZConfig.SchemaError(
                "schema component not found: " + `package`)
        urls = [fn]
        for fn in os.listdir(dirname):
            if fn == "schema.xml":
                continue
            path = os.path.join(dirname, fn, "schema.xml")
            if os.path.exists(path):
                urls.append(path)
        return urls


class ConfigLoader(BaseLoader):
    def __init__(self, schema):
        if schema.istypegroup():
            raise ZConfig.SchemaError(
                "cannot check a configuration an abstract type")
        BaseLoader.__init__(self)
        self.schema = schema

    def loadResource(self, resource):
        self.handlers = []
        sm = matcher.SchemaMatcher(self.schema, self.handlers)
        self._parse_resource(sm, resource)
        return sm.finish(), CompositeHandler(self.handlers, self.schema)

    # config parser support API

    def startSection(self, parent, type, name, delegatename):
        if delegatename:
            raise NotImpementedError("section delegation is not yet supported")
        t = self.schema.gettype(type)
        if t.istypegroup():
            raise ZConfig.ConfigurationError(
                "concrete sections cannot match abstract section types;"
                " found abstract type " + `type`)
        ci = parent.type.getsectioninfo(type, name)
        assert not ci.istypegroup()
        if not ci.isAllowedName(name):
            raise ZConfig.ConfigurationError(
                "%s is not an allowed name for %s sections"
                % (`name`, `ci.sectiontype.name`))
        return matcher.SectionMatcher(ci, t, name, self.handlers)

    def endSection(self, parent, type, name, delegatename, matcher):
        assert not delegatename
        sectvalue = matcher.finish()
        parent.addSection(type, name, sectvalue)

    def includeConfiguration(self, section, url):
        r = self.openResource(url)
        self._parse_resource(section, r)

    # internal helper

    def _parse_resource(self, matcher, resource):
        from ZConfig.cfgparser import ZConfigParser
        parser = ZConfigParser(resource, self)
        parser.parse(matcher)


class CompositeHandler:
    def __init__(self, handlers, schema):
        self._handlers = handlers
        self._convert = schema.registry.get("basic-key")

    def __call__(self, handlermap):
        d = {}
        for name, callback in handlermap.items():
            n = self._convert(name)
            if d.has_key(n):
                raise ZConfig.ConfigurationError(
                    "handler name not unique when converted to a basic-key: "
                    + `name`)
            d[n] = callback
        L = []
        for handler, value in self._handlers:
            if not d.has_key(handler):
                L.append(handler)
        if L:
            raise ZConfig.ConfigurationError(
                "undefined handlers: " + ", ".join(L))
        for handler, value in self._handlers:
            f = d[handler]
            if f is not None:
                f(value)

    def __len__(self):
        return len(self._handlers)


class Resource:
    def __init__(self, file, url, fragment=None):
        self.file = file
        self.url = url
        self.fragment = fragment

    def close(self):
        if self.file is not None:
            self.file.close()
            self.file = None
            self.closed = True

    def __getattr__(self, name):
        return getattr(self.file, name)
