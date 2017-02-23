##############################################################################
#
# Copyright (c) 2016 Zope Foundation and Contributors.
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

import sys

PY3 = sys.version_info[0] >= 3

# Native string object IO
if str is not bytes:
    from io import StringIO as NStringIO
    string_types = str
else:
    # Python 2
    from io import BytesIO as NStringIO
    string_types = str, unicode

NStringIO = NStringIO

from io import StringIO
from io import BytesIO

def TextIO(text):
    "Return StringIO or BytesIO as appropriate"
    return BytesIO(text) if isinstance(text, bytes) else StringIO(text)

try:
    import urllib2
except ImportError:
    # Python 3 support.
    import urllib.request as urllib2

urllib2 = urllib2

try:
    from urllib import pathname2url
except ImportError:
    # Python 3 support.
    from urllib.request import pathname2url

pathname2url = pathname2url

try:
    import urlparse as urlparse
except ImportError:
    # Python 3 support
    import urllib.parse as urlparse

urlparse = urlparse

if PY3: # pragma: no cover
    import builtins
    exec_ = getattr(builtins, "exec")
    text_type = str
    binary_type = bytes
    maxsize = sys.maxsize

    def reraise(tp, value, tb=None): #pragma NO COVER
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

else: # pragma: no cover
    text_type = unicode
    binary_type = bytes
    maxsize = sys.maxint

    def exec_(code, globs=None, locs=None): #pragma NO COVER
        """Execute code in a namespace."""
        if globs is None:
            frame = sys._getframe(1)
            globs = frame.f_globals
            if locs is None:
                locs = frame.f_locals
            del frame
        elif locs is None:
            locs = globs
        exec("""exec code in globs, locs""")

    exec_("""def reraise(tp, value, tb=None):
    raise tp, value, tb
""")


def raise_with_same_tb(exception):
	"Raise an exception having the current traceback (if there is one)"
	reraise(type(exception), exception, sys.exc_info()[2])

import abc
# workaround the metaclass diff in Py2/Py3
AbstractBaseClass = abc.ABCMeta('AbstractBaseClass', (object,), {})
