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

    return tn

class explain(object):
    done = []

    def __call__(self, st, file=None):
        if st.name in self.done: # pragma: no cover
            return

        self.done.append(st.name)

        out = file or sys.stdout

        if st.description:
            print(st.description, file=out)
        for sub in st.getsubtypenames():
            print('<dl>', file=out)
            printContents(None, st.getsubtype(sub), file=file)
            print('</dl>', file=out)

explain = explain()

def printSchema(schema, out):
    print('<dl>', file=out)
    for child in schema:
        printContents(*child, file=out)
    print('</dl>', file=out)

def printContents(name, info, file=None):
    out = file or sys.stdout

    if isinstance(info, SectionType):
        print('<dt><b><i>', info.name, '</i></b> (%s)</dt>' % dt(info.datatype), file=out)
        print('<dd>', file=out)
        if info.description:
            print(info.description, file=out)
        print('<dl>', file=out)
        for sub in info:
            printContents(*sub, file=out) # pragma: no cover
        print('</dl></dd>', file=out)
    elif isinstance(info, SectionInfo):
        st = info.sectiontype
        if st.isabstract():
            print('<dt><b><i>', st.name, '</i>', info.name, '</b></dt>', file=out)
            print('<dd>', file=out)
            if info.description:
                print(info.description, file=out)
            explain(st, file=out)
            print('</dd>', file=out)
        else:
            print('<dt><b>', info.attribute, info.name, '</b>', file=out)
            print('(%s)</dt>' % dt(info.datatype), file=out)
            print('<dd><dl>', file=out)
            for sub in info.sectiontype:
                printContents(*sub, file=out)
            print('</dl></dd>', file=out)
    elif isinstance(info, AbstractType):
        print('<dt><b><i>', info.name, '</i></b>', file=out)
        print('<dd>', file=out)
        if info.description:
            print(info.description, file=out) # pragma: no cover
        explain(info, file=out)
        print('</dd>', file=out)
    else:
        print('<dt><b>',info.name, '</b>', '(%s)' % dt(info.datatype), file=out)
        default = info.getdefault()
        if isinstance(default, ValueInfo):
            print('(default: %r)' % esc(default.value), file=out)
        elif default is not None:
            print('(default: %r)' % esc(default), file=out)
        if info.metadefault:
            print('(metadefault: %s)' % info.metadefault, file=out)
        print('</dt>', file=out)
        if info.description:
            print('<dd>',info.description,'</dd>', file=out)

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
    printSchema(iter(schema) if not args.package else schema.itertypes(), out)
    print('</body></html>', file=out)

    return 0
