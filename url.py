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
"""urlparse-like helpers that normalize file: URLs.

ZConfig and urllib2 expect file: URLs to consistently use the '//'
hostpart seperator; the functions here enforce this constraint.
"""

import posixpath as _posixpath
import urlparse as _urlparse

from urllib import splittype as _splittype
from urlparse import urlsplit


def urlnormalize(url):
    parts = urlsplit(url)
    if not parts[0]:
        raise ValueError("invalid URL, or file does not exist:\n"
                         + repr(url))
    url = urlunsplit(parts)
    if url.startswith("file:/") and not url.startswith("file:///"):
        url = "file://" + url[5:]
    return url


def urlunsplit(parts):
    url = _urlparse.urlunsplit(parts)
    if (  parts[0] == "file"
          and url.startswith("file:/")
          and not url.startswith("file:///")):
        url = "file://" + url[5:]
    return url


def urldefrag(url):
    url, fragment = _urlparse.urldefrag(url)
    return urlnormalize(url), fragment


def urljoin(base, relurl):
    url = _urlparse.urljoin(base, relurl)
    if url.startswith("file:/") and not url.startswith("file:///"):
        url = "file://" + url[5:]
    return url
