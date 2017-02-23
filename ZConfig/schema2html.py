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
import itertools
import sys
import cgi

import ZConfig.loader

from ZConfig.datatypes import null_conversion
from ZConfig.info import SectionType
from ZConfig.info import SectionInfo
from ZConfig.info import ValueInfo
from ZConfig.info import AbstractType

from ZConfig._compat import string_types

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
        self.stream = stream or sys.stdout
        self._dt = schema.registry.find_name

    def write(self, *args):
        print(*args, file=self.stream)

    def esc(self, x):
        return cgi.escape(str(x))

    @contextmanager
    def _simple_tag(self, tag):
        self.write("<%s>" % tag)
        yield
        self.write("</%s>" % tag)

    def item_list(self):
        return self._simple_tag("dl")

    def _describing(self, description, after):
        if description is not _MARKER:
            with self.described_as():
                self.description(description)
                if after:
                    after()

    @contextmanager
    def describing(self, description=_MARKER, after=None):
        with self._simple_tag("dt"):
            yield
        self._describing(description, after)

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

    @contextmanager
    def body(self):
        self.write('''<html><body>
        <style>
        dl {margin: 0 0 1em 0;}
        </style>
        ''')
        yield
        self.write('</body></html>')


class SchemaPrinter(object):

    SchemaFormatter = SchemaFormatter

    def __init__(self, schema, stream=None):
        self.schema = schema
        stream = stream or sys.stdout
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
                if isinstance(info, SectionInfo):
                    if info.sectiontype.isabstract():
                        yield name, info

                    # XXX: This isn't catching everything. Witness the
                    # relstorage component.
                elif isinstance(info, SectionType):
                    for x in abstract_sections(info):
                        yield x
        return itertools.chain(abstract_sections(everything()), everything())

    def printSchema(self):
        # side-effect of building may be printing
        self.buildSchema()

    def buildSchema(self):
        seen = set() # prevent duplicates at the top-level
        # as we find multiple abstract types
        with self.fmt.body():
            with self.fmt.item_list():
                for name, info in self._iter_schema_items():
                    if info in seen:
                        continue
                    seen.add(info)
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

try:
    from docutils import nodes
    import docutils.utils
    import docutils.frontend
    import docutils.parsers.rst
    from docutils.parsers.rst import Directive
except ImportError: # pragma: no cover
    RstSchemaPrinter = None
    RstSchemaFormatter = None
else:
    class RstSchemaFormatter(SchemaFormatter):

        settings = None

        def __init__(self, schema, stream=None):
            super(RstSchemaFormatter, self).__init__(schema, stream)
            self.document = None
            self._current_node = None
            self._nodes = []

        def esc(self, text):
            return text

        def _parsed(self, text):
            document = docutils.utils.new_document(
                "Schema",
                settings=self.settings or docutils.frontend.OptionParser(
                    components=(docutils.parsers.rst.Parser,)
                    ).get_default_values())
            parser = docutils.parsers.rst.Parser()
            parser.parse(text, document)
            return document.children

        def write(self, *texts):
            for text in texts:
                if isinstance(text, string_types):
                    self._current_node += nodes.Text(' ' + text + ' ', text)
                else:
                    # Already parsed
                    self._current_node += text

        def description(self, text):
            if not text:
                return

            # Aggressively dedent the text to avoid producing unwanted
            # definition lists.
            # XXX: This is probably *too* aggressive.
            texts = []
            parts = text.split('\n')
            for p in parts:
                p = p.strip()
                if not p:
                    texts.append('\n')
                else:
                    texts.append(p)
            text = '\n'.join(texts)
            self.write(self._parsed(text))


        @contextmanager
        def item_list(self):
            old_node = self._current_node
            self._current_node = nodes.definition_list()
            old_node += self._current_node
            yield
            self._current_node = old_node


        @contextmanager
        def describing(self, description=_MARKER, after=None):
            dl = self._current_node
            assert isinstance(dl, nodes.definition_list), dl
            item = nodes.definition_list_item()
            dl += item
            term = nodes.term()
            item += term
            self._current_node = term

            yield

            # We must now have either a description (so we call
            # described_as) or they must call described_as
            # des
            self._current_node = item

            self._describing(description, after)


        @contextmanager
        def described_as(self):
            item = self._current_node
            assert isinstance(item, nodes.definition_list_item), item

            definition = nodes.definition()
            para = nodes.paragraph()
            definition += para
            item += definition
            self._current_node = para

            yield

            # When this is done, we're back to the list
            self._current_node = item.parent

        def abstract_name(self, name):
            self._current_node += nodes.emphasis(text=name, rawsource=name)

        def concrete_name(self, name):
            self._current_node += nodes.strong(text=name, rawsource=name)

        def concrete_section_name(self, *name):
            name = ' '.join(name)
            return self.concrete_name("<" + name + ">")

        @contextmanager
        def body(self):
            self.document = self._current_node = docutils.utils.new_document(
                "Schema",
                settings=self.settings or docutils.frontend.OptionParser(
                    components=(docutils.parsers.rst.Parser,)
                    ).get_default_values())
            yield

    class RstSchemaPrinter(SchemaPrinter):
        SchemaFormatter = RstSchemaFormatter

        def printSchema(self):
            super(RstSchemaPrinter, self).printSchema()
            print(self.fmt.document.pformat(), file=self.fmt.stream)


    class SchemaToRstDirective(Directive):
        required_arguments = 1

        def run(self): # pragma: no cover
            schema = _load_schema(self.arguments[0], True, 'component.xml')

            printer = RstSchemaPrinter(schema)
            try:
                printer.fmt.settings = self.state.document.settings
            except AttributeError:
                pass
            printer.buildSchema()

            return printer.fmt.document.children

    def setup(app): # pragma: no cover
        "Sphinx extension entry point to add the zconfig directive."
        app.add_directive("zconfig", SchemaToRstDirective)

def _load_schema(schema, package, package_file):
    if not package:
        schema_reader = argparse.FileType('r')(schema)
    else:
        schema_template = "<schema><import package='%s' file='%s' /></schema>" % (
            schema, package_file)
        from ZConfig._compat import TextIO
        schema_reader = TextIO(schema_template)

    schema = ZConfig.loader.loadSchemaFile(schema_reader)
    return schema

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

    if RstSchemaFormatter:
        argparser.add_argument(
            "--format",
            action="store",
            choices=('html', 'xml'), # XXX Can we get actual valid RST out?
            default="HTML",
            help="What output format to produce"
        )

    args = argparser.parse_args(argv)

    out = args.out or sys.stdout

    schema = _load_schema(args.schema, args.package, args.package_file)

    printer_factory = SchemaPrinter
    if hasattr(args, 'format') and args.format == 'xml':
        printer_factory = RstSchemaPrinter


    printer_factory(schema, out).printSchema()


    return 0
