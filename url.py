"""urlparse-like helpers that support the zconfig scheme."""

import posixpath as _posixpath
import urlparse as _urlparse

from urllib import splittype as _splittype


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
    parts = urlsplit(url)
    if parts[0] == "zconfig":
        return "zconfig:" + parts[2], parts[4]
    else:
        url, fragment = _urlparse.urldefrag(url)
        return urlnormalize(url), fragment


def urljoin(base, relurl):
    scheme = _splittype(base)[0]
    if scheme != "zconfig":
        url = _urlparse.urljoin(base, relurl)
        if url.startswith("file:/") and not url.startswith("file:///"):
            url = "file://" + url[5:]
        return url
    relscheme = _splittype(relurl)[0]
    if relscheme and relscheme != "zconfig":
        return _urlparse.urljoin(base, relurl)
    baseparts = urlsplit(base)
    relparts = urlsplit(relurl, "zconfig")
    if relparts[2]:
        d = _posixpath.dirname(baseparts[2])
        if d:
            d += "/"
        path = _posixpath.normpath(_posixpath.join(d, relparts[2]))
    else:
        path = baseparts[2]
    parts = path.split('/')
    if '..' in parts:
        raise ValueError("zconfig URIs cannot include '..' references: "
                         + `path`)
    s = "zconfig:" + path
    if relparts[4]:
        s += "#" + relparts[4]
    return s


def urlsplit(url, scheme=''):
    stated_scheme = _splittype(url)[0]
    scheme = stated_scheme or scheme
    parts = _urlparse.urlsplit(url, scheme=scheme)
    if scheme == "zconfig":
        path = parts[2]
        if stated_scheme:
            # These constraints only apply to absolute zconfig: URLs
            if not path:
                # Require a non-empty path; empty path is ok for
                # relative URL ("#frag").
                raise ValueError(
                    "zconfig URIs require a non-empty path component")
            if '..' in path.split('/'):
                raise ValueError(
                    "zconfig URIs cannot include '..' references: " + `url`)
        # Split the fragment ourselves since the urlparse module
        # doesn't know about the zconfig: scheme.
        if '#' in path:
            path, fragment = path.split('#', 1)
            parts = "zconfig", '', path, '', fragment
        if path[:1] == '/':
            raise ValueError(
                "path component of zconfig: URIs may not start with '/'")
        if '?' in path:
            raise ValueError("zconfig: URIs may not contain queries: "
                             + `url`)
    return parts
