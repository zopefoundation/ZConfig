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
import functools
import itertools
import sys
import cgi

import ZConfig.loader


from ZConfig.info import SectionType
from ZConfig.info import SectionInfo
from ZConfig.info import ValueInfo
from ZConfig.info import AbstractType

def esc(x):
    return cgi.escape(str(x))

class _VisitorBuilder(object):

    def __init__(self):
        self.visitors = []

    def __call__(self, Type):
        def dec(func):
            self.visitors.append((Type, func))
            return func
        return dec


class SchemaPrinter(object):

    def __init__(self, schema, stream=None):
        self.schema = schema
        stream = stream or sys.stdout
        self.write = functools.partial(print, file=stream)
        self._explained = set()
        self._dt = schema.registry.find_name
        self._seen_typenames = set()

    def _explain(self, st):
        if st.name in self._explained: # pragma: no cover
            return

        self._explained.add(st.name)

        if st.description:
            self.write(st.description)
        for sub in st.getsubtypenames():
            self.write('<dl>')
            self.visit(None, st.getsubtype(sub))
            self.write('</dl>')

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
        self.write('<dl>')
        for name, info in self._iter_schema_items():
            self.visit(name, info)
        self.write('</dl>')

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
        self.write('<dt><b><i>', info.name, '</i></b> (%s)</dt>' % self._dt(info.datatype))
        self.write('<dd>')
        if info.description:
            self.write(info.description)

        self.write('<dl>')
        for sub in info:
            self.visit(*sub) # pragma: no cover
        self.write('</dl>')
        self.write('</dd>')

    @TypeVisitor(SectionInfo)
    def _visit_SectionInfo(self, name, info):
        st = info.sectiontype
        if st.isabstract():
            self.write('<dt><b><i>', st.name, '</i>', info.name, '</b></dt>')
            self.write('<dd>')
            if info.description:
                self.write(info.description)
            self._explain(st)
            self.write('</dd>')
        else:
            self.write('<dt><b>', info.attribute, info.name, '</b>')
            self.write('(%s)</dt>' % self._dt(info.datatype))
            self.write('<dd><dl>')
            for sub in info.sectiontype:
                self.visit(*sub)
            self.write('</dl></dd>')

    @TypeVisitor(AbstractType)
    def _visit_AbstractType(self, name, info):
        self.write('<dt><b><i>', info.name, '</i></b>')
        self.write('<dd>')
        if info.description:
            self.write(info.description) # pragma: no cover
        self._explain(info)
        self.write('</dd>')

    def _visit_default(self, name, info):
        # KeyInfo or MultiKeyInfo
        self.write('<dt><b>',info.name, '</b>', '(%s)' % self._dt(info.datatype))
        default = info.getdefault()
        if isinstance(default, ValueInfo):
            self.write('(default: %r)' % esc(default.value))
        elif default is not None:
            self.write('(default: %r)' % esc(default))
        if info.metadefault:
            self.write('(metadefault: %s)' % info.metadefault)
        self.write('</dt>')
        if info.description:
            self.write('<dd>', info.description,'</dd>')

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
