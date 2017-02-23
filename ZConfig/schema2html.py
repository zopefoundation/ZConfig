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
import sys
import cgi

import ZConfig.loader


from ZConfig.info import SectionType
from ZConfig.info import SectionInfo
from ZConfig.info import ValueInfo
from ZConfig.info import AbstractType

def esc(x):
    return cgi.escape(str(x))

def dt(x):

    tn = type(x).__name__

    if isinstance(x, type):
        return '%s %s' % (tn, x.__module__ + '.' + x.__name__)

    if hasattr(x, '__name__'):
        return '%s %s' % (tn, x.__name__)

    return tn # pragma: no cover


class SchemaPrinter(object):

    def __init__(self, schema, stream=None):
        self.schema = schema
        stream = stream or sys.stdout
        self.write = functools.partial(print, file=stream)
        self._explained = []

    def _explain(self, st):
        if st.name in self._explained: # pragma: no cover
            return

        self._explained.append(st.name)


        if st.description:
            self.write(st.description)
        for sub in st.getsubtypenames():
            self.write('<dl>')
            self.printContents(None, st.getsubtype(sub))
            self.write('</dl>')

    def printSchema(self):
        self.write('<dl>')
        for child in self.schema:
            self.printContents(*child)
        self.write('</dl>')

    def printContents(self, name, info):
        if isinstance(info, SectionType):
            self.write('<dt><b><i>', info.name, '</i></b> (%s)</dt>' % dt(info.datatype))
            self.write('<dd>')
            if info.description:
                self.write(info.description)
            self.write('<dl>')
            for sub in info:
                self.printContents(*sub) # pragma: no cover
            self.write('</dl></dd>')
        elif isinstance(info, SectionInfo):
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
                self.write('(%s)</dt>' % dt(info.datatype))
                self.write('<dd><dl>')
                for sub in info.sectiontype:
                    self.printContents(*sub)
                self.write('</dl></dd>')
        elif isinstance(info, AbstractType):
            self.write('<dt><b><i>', info.name, '</i></b>')
            self.write('<dd>')
            if info.description:
                self.write(info.description) # pragma: no cover
            self._explain(info)
            self.write('</dd>')
        else:
            self.write('<dt><b>',info.name, '</b>', '(%s)' % dt(info.datatype))
            default = info.getdefault()
            if isinstance(default, ValueInfo):
                self.write('(default: %r)' % esc(default.value))
            elif default is not None:
                self.write('(default: %r)' % esc(default))
            if info.metadefault:
                self.write('(metadefault: %s)' % info.metadefault)
            self.write('</dt>')
            if info.description:
                self.write('<dd>',info.description,'</dd>')

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
    SchemaPrinter(iter(schema) if not args.package else schema.itertypes(), out).printSchema()
    print('</body></html>', file=out)

    return 0
