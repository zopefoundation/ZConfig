##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
from __future__ import print_function

import argparse
from contextlib import contextmanager
import functools
import itertools
import sys
import cgi

import ZConfig.loader

from ZConfig.datatypes import null_conversion
from ZConfig.info import SectionType
from ZConfig.info import SectionInfo
from ZConfig.info import ValueInfo
from ZConfig.info import AbstractType

class _VisitorBuilder(object):

    def __init__(self):
        self.visitors = []

    def __call__(self, Type):
        def dec(func):
            self.visitors.append((Type, func))
            return func
        return dec

_MARKER = object()

class SchemaFormatter(object):

    def __init__(self, schema, stream=None):
        stream = stream or sys.stdout
        self.write = functools.partial(print, file=stream)
        self._dt = schema.registry.find_name

    def esc(self, x):
        return cgi.escape(str(x))

    @contextmanager
    def _simple_tag(self, tag):
        self.write("<%s>" % tag)
        yield
        self.write("</%s>" % tag)

    def item_list(self):
        return self._simple_tag("dl")

    @contextmanager
    def describing(self, description=_MARKER, after=None):
        with self._simple_tag("dt"):
            yield

        if description is not _MARKER:
            with self.described_as():
                self.description(description)
                if after:
                    after()

    def describing_name(self, concrete_name,
                        description=_MARKER, datatype=None,
                        **kwargs):
        with self.describing(description):
            self.concrete_name(concrete_name)
            self.datatype(datatype)

            for k, v in sorted(kwargs.items()):
                if v:
                    self.write(self.esc("(%s: %s)" % (k, v)))

    def description(self, description):
        if description:
            self.write(self.esc(description))

    def described_as(self):
        return self._simple_tag("dd")

    def abstract_name(self, name):
        self.write("<b><i>", name, "</b></i>")

    def concrete_name(self, *name):
        self.write("<b>", *name)
        self.write("</b>")

    def concrete_section_name(self, *name):
        name = ' '.join(name)
        self.write("<b>", self.esc("<%s>" % name), "</b>")

    def datatype(self, datatype):
        self.write("(%s)" % self._dt(datatype))

class SchemaPrinter(object):

    SchemaFormatter = SchemaFormatter

    def __init__(self, schema, stream=None):
        self.schema = schema
        stream = stream or sys.stdout
        self.write = functools.partial(print, file=stream)
        self._explained = set()
        self._seen_typenames = set()
        self.fmt = self.SchemaFormatter(schema, stream)


    def _explain(self, st):
        if st.name in self._explained: # pragma: no cover
            return

        self._explained.add(st.name)

        self.fmt.description(st.description)
        for sub in st.getsubtypenames():
            with self.fmt.item_list():
                self.visit(None, st.getsubtype(sub))

    def _iter_schema_items(self):
        def everything():
            return itertools.chain(self.schema.itertypes(),
                                   self.schema)
        # The abstract types tend to be the most important. Since
        # we only document a concrete type the first time we find it,
        # and we can find extensions of abstract types beneath
        # the abstract type which is itself buried under a concrete section,
        # all the different permutations would be only documented once under
        # that section. By exposing these first, they get documented at the top-level,
        # and each concrete section that uses the abstract type gets a reference
        # to it.
        def abstract_sections(base):
            for name, info in base:
                if isinstance(info, SectionInfo) and info.sectiontype.isabstract():
                    yield name, info
                elif isinstance(info, SectionType):
                    for x in abstract_sections(info):
                        yield x
        return itertools.chain(abstract_sections(everything()), everything())


    def printSchema(self):
        with self.fmt.item_list():
            for name, info in self._iter_schema_items():
                self.visit(name, info)

    TypeVisitor = _VisitorBuilder()
    visitors = TypeVisitor.visitors

    def visit(self, name, info):
        for t, f in self.visitors:
            if isinstance(info, t):
                f(self, name, info)
                break
        else:
            self._visit_default(name, info)

    @TypeVisitor(SectionType)
    def _visit_SectionType(self, name, info):
        if info.name in self._seen_typenames:
            return
        self._seen_typenames.add(info.name)
        with self.fmt.describing():
            if info.datatype is not null_conversion:
                self.fmt.concrete_section_name(info.name)
            else:
                self.fmt.abstract_name(info.name)
            self.fmt.datatype(info.datatype)

        with self.fmt.described_as():
            self.fmt.description(info.description)

            with self.fmt.item_list():
                for sub in info:
                    self.visit(*sub) # pragma: no cover


    @TypeVisitor(SectionInfo)
    def _visit_SectionInfo(self, name, info):
        st = info.sectiontype
        if st.isabstract():
            with self.fmt.describing(info.description, lambda: self._explain(st)):
                self.fmt.abstract_name(st.name)
                self.fmt.concrete_name(info.name)

        else:
            with self.fmt.describing():
                self.fmt.concrete_section_name(info.attribute, info.name)
                self.fmt.datatype(info.datatype)

            with self.fmt.described_as():
                with self.fmt.item_list():
                    for sub in info.sectiontype:
                        self.visit(*sub)


    @TypeVisitor(AbstractType)
    def _visit_AbstractType(self, name, info):
        with self.fmt.describing(info.description, lambda: self._explain(info)):
            self.fmt.abstract_name(info.name)

    def _visit_default(self, name, info):
        # KeyInfo or MultiKeyInfo
        default = info.getdefault()
        if isinstance(default, ValueInfo):
            default = default.value

        self.fmt.describing_name(info.name, info.description, info.datatype,
                                 default=default, metadefault=info.metadefault)

    del TypeVisitor

def main(argv=None):
    argv = argv or sys.argv[1:]

    argparser = argparse.ArgumentParser(
        description="Print an HTML version of a schema")
    argparser.add_argument(
        "schema",
        metavar='[SCHEMA-OR-PACKAGE]',
        help="The schema to print. By default, a file. Optionally, a Python package."
             " If not given, defaults to reading a schema file from stdin",
        default="-"
        )
    argparser.add_argument(
        "--out", "-o",
        help="Write the schema to this file; if not given, write to stdout",
        type=argparse.FileType('w'))
    argparser.add_argument(
        "--package",
        action='store_true',
        default=False,
        help="The SCHEMA-OR-PACKAGE argument indicates a Python package instead of a file."
             " The component.xml (by default) from the package will be read.")
    argparser.add_argument(
        "--package-file",
        action="store",
        default="component.xml",
        help="When PACKAGE is given, this can specify the file inside it to load.")

    args = argparser.parse_args(argv)

    out = args.out or sys.stdout

    if not args.package:
        schema_reader = argparse.FileType('r')(args.schema)
    else:
        schema_template = "<schema><import package='%s' file='%s' /></schema>" % (
            args.schema, args.package_file)
        from ZConfig._compat import TextIO
        schema_reader = TextIO(schema_template)

    schema = ZConfig.loader.loadSchemaFile(schema_reader)

    print('''<html><body>
    <style>
    dl {margin: 0 0 1em 0;}
    </style>
    ''', file=out)
    SchemaPrinter(schema, out).printSchema()
    print('</body></html>', file=out)

    return 0
