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
from __future__ import absolute_import

import contextlib
import sys
import unittest

try:
    # Note that we're purposely using the old
    # StringIO object on Python 2 because it auto-converts
    # Unicode to str, which io.BytesIO and io.StringIO don't
    # but which normal printing to default sys.stdout *does*
    from cStringIO import StringIO
except ImportError:
    from ZConfig._compat import NStringIO as StringIO


from ZConfig import schema2html

from .support import input_file
from .support import with_stdin_from_input_file


@contextlib.contextmanager
def stdout_replaced(buf):
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        yield
    finally:
        sys.stdout = old_stdout


def run_transform(*args):
    if '--out' not in args and '-o' not in args:
        buf = StringIO()
        with stdout_replaced(buf):
            schema2html.main(args)
        return buf
    return schema2html.main(args) # pragma: no cover



class TestSchema2HTML(unittest.TestCase):

    def test_no_schema(self):
        self.assertRaises(SystemExit,
                          run_transform)

    def test_schema_only(self):
        res = run_transform(input_file('simple.xml'))
        self.assertIn('</html>', res.getvalue())

    @with_stdin_from_input_file('simple.xml')
    def test_schema_only_redirect(self):
        res = run_transform("-")
        self.assertIn('</html>', res.getvalue())

    def test_cover_all_schemas(self):
        for name in ('base-datatype1.xml',
                     'base-datatype2.xml',
                     'base-keytype1.xml',
                     'base-keytype2.xml',
                     'base.xml',
                     'library.xml',
                     'simplesections.xml',):
            res = run_transform(input_file(name))
            self.assertIn('</html>', res.getvalue())

    def test_cover_logging_components(self):
        res = run_transform('--package', 'ZConfig.components.logger')
        self.assertIn('eventlog', res.getvalue())

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
