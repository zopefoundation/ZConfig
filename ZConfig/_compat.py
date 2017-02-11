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
    from io import StringIO as _NStringIO
else:
    # Python 2
    from io import BytesIO as _NStringIO

NStringIO = _NStringIO

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

if PY3: # pragma: no cover
    import builtins
    exec_ = getattr(builtins, "exec")


    def reraise(tp, value, tb=None): #pragma NO COVER
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

else: # pragma: no cover
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
