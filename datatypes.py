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
"""Selection of standard datatypes for ZConfig."""

import re
import sys
import os

try:
    True
except NameError:
    True = 1
    False = 0


class MemoizedConversion:
    """Conversion helper that caches the results of expensive conversions."""

    def __init__(self, conversion):
        self._memo = {}
        self._conversion = conversion

    def __call__(self, value):
        try:
            return self._memo[value]
        except KeyError:
            v = self._conversion(value)
            self._memo[value] = v
            return v


class RangeCheckedConversion:
    """Conversion helper that range checks another conversion."""

    def __init__(self, conversion, min=None, max=None):
        self._min = min
        self._max = max
        self._conversion = conversion

    def __call__(self, value):
        v = self._conversion(value)
        if self._min is not None and v < self._min:
            raise ValueError("%s is below lower bound (%s)"
                             % (`v`, `self._min`))
        if self._max is not None and v > self._max:
            raise ValueError("%s is above upper bound (%s)"
                             % (`v`, `self._max`))
        return v


class RegularExpressionConversion:
    def __init__(self, regex):
        self._rx = re.compile(regex)

    def __call__(self, value):
        m = self._rx.match(value)
        if m and m.group() == value:
            return value
        else:
            raise ValueError("value did not match regular expression: "
                             + `value`)


def check_locale(value):
    import locale
    prev = locale.setlocale(locale.LC_ALL)
    try:
        try:
            locale.setlocale(locale.LC_ALL, value)
        finally:
            locale.setlocale(locale.LC_ALL, prev)
    except locale.Error:
        raise ValueError(
            'The specified locale "%s" is not supported by your system.\n'
            'See your operating system documentation for more\n'
            'information on locale support.' % value)
    else:
        return value


class BasicKeyConversion(RegularExpressionConversion):
    def __init__(self):
        RegularExpressionConversion.__init__(self, "[a-zA-Z][-._a-zA-Z0-9]*")

    def __call__(self, value):
        value = str(value)
        return RegularExpressionConversion.__call__(self, value).lower()


class IdentifierConversion(RegularExpressionConversion):
    def __init__(self):
        RegularExpressionConversion.__init__(self, "[_a-zA-Z][_a-zA-Z0-9]*")


class LogLevelConversion:
    # This uses the 'logging' package conventions; only makes sense
    # for Zope 2.7 (and newer) and Zope 3.  Not sure what the
    # compatibility should be.

    _levels = {
        "critical": 50,
        "fatal": 50,
        "error": 40,
        "warn": 30,
        "info": 20,
        "debug": 10,
        "all": 0,
        }

    def __call__(self, value):
        s = str(value).lower()
        if self._levels.has_key(s):
            return self._levels[s]
        else:
            v = int(s)
            if v < 0 or v > 50:
                raise ValueError("log level not in range: " + `v`)
            return v


if sys.version[:3] < "2.3":
    def integer(value):
        try:
            return int(value)
        except ValueError:
            return long(value)
else:
    integer = int


def null_conversion(value):
    return value


def asBoolean(s):
    """Convert a string value to a boolean value."""
    ss = str(s).lower()
    if ss in ('yes', 'true', 'on'):
        return True
    elif ss in ('no', 'false', 'off'):
        return False
    else:
        raise ValueError("not a valid boolean value: " + repr(s))


port_number = RangeCheckedConversion(integer, min=1, max=0xffff).__call__


def inet_address(s):
    # returns (host, port) tuple
    host = ''
    port = None
    if ":" in s:
        host, s = s.split(":", 1)
        if s:
            port = port_number(s)
        host = host.lower()
    else:
        try:
            port = port_number(s)
        except ValueError:
            host = s.lower()
    return host, port


class SocketAddress:
    def __init__(self, s):
        # returns (family, address) tuple
        import socket
        if "/" in s:
            self.family = getattr(socket, "AF_UNIX", None)
            self.address = s
        else:
            self.family = socket.AF_INET
            self.address = inet_address(s)

def float_conversion(v):
    if isinstance(v, type('')) or isinstance(v, type(u'')):
        if v.lower() in ["inf", "-inf", "nan"]:
            raise ValueError(`v` + " is not a portable float representation")
    return float(v)

class IpaddrOrHostname(RegularExpressionConversion):
    def __init__(self):
        # IP address regex from the Perl Cookbook, Recipe 6.23 (revised ed.)
        # We allow underscores in hostnames although this is considered
        # illegal according to RFC1034.
        expr = (r"(^(\d|[01]?\d\d|2[0-4]\d|25[0-5])\." #ipaddr
                r"(\d|[01]?\d\d|2[0-4]\d|25[0-5])\." #ipaddr cont'd
                r"(\d|[01]?\d\d|2[0-4]\d|25[0-5])\." #ipaddr cont'd
                r"(\d|[01]?\d\d|2[0-4]\d|25[0-5])$)" #ipaddr cont'd
                r"|([A-Za-z_][-A-Za-z0-9_.]*[-A-Za-z0-9_])") # or hostname
        RegularExpressionConversion.__init__(self, expr)

    def __call__(self, value):
        return RegularExpressionConversion.__call__(self, value).lower()

def existing_directory(v):
    if os.path.isdir(v):
        return v
    raise ValueError, '%s is not an existing directory' % v

def existing_path(v):
    if os.path.exists(v):
        return v
    raise ValueError, '%s is not an existing path' % v

def existing_file(v):
    if os.path.exists(v):
        return v
    raise ValueError, '%s is not an existing file' % v

def existing_dirpath(v):
    if not os.path.split(v)[0]:
        # relative pathname
        return v
    dir = os.path.dirname(v)
    if os.path.isdir(dir):
        return v
    raise ValueError, ('The directory named as part of the path %s '
                       'does not exist.' % v)

def parse_constructor(v):
    parenmsg = (
        'Invalid constructor (unbalanced parenthesis in "%s")' % v
        )
    openparen = v.find('(')
    if openparen < 0:
        raise ValueError(parenmsg)
    klass = v[:openparen]
    if not v.endswith(')'):
        raise ValueError(parenmsg)
    arglist = v[openparen+1:-1]
    return klass, arglist

def get_arglist(s):
    # someone could do a better job at this.
    pos = []
    kw = {}
    args = s.split(',')
    args = filter(None, args)
    while args:
        arg = args.pop(0)
        try:
            if '=' in arg:
                k,v=arg.split('=', 1)
                k = k.strip()
                v = v.strip()
                kw[k] = eval(v)
            else:
                arg = arg.strip()
                pos.append(eval(arg))
        except SyntaxError:
            if not args:
                raise
            args[0] = '%s, %s' % (arg, args[0])
    return pos, kw

def constructor_conversion(v):
    klass, arglist = parse_constructor(v)
    pos, kw = get_arglist(arglist)
    return klass, pos, kw

def space_sep_key_value_conversion(v):
    l = v.split(' ', 1)
    if len(l) < 2:
        l.append('')
    return l


class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers.  If no suffixes
    # match, default is the multiplier.  Matches are case insensitive.  Return
    # values are in the fundamental unit.
    def __init__(self, d, default=1):
        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d.keys():
            if self._keysz is None:
                self._keysz = len(k)
            else:
                assert self._keysz == len(k)

    def __call__(self, v):
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:
                return int(v[:-self._keysz]) * m
        return int(v) * self._default

stock_datatypes = {
    "boolean":           asBoolean,
    "identifier":        IdentifierConversion(),
    "integer":           integer,
    "float":             float_conversion,
    "string":            str,
    "null":              null_conversion,
    "locale":            MemoizedConversion(check_locale),
    "port-number":       port_number,
    "basic-key":         BasicKeyConversion(),
    "logging-level":     LogLevelConversion(),
    "inet-address":      inet_address,
    "socket-address":    SocketAddress,
    "ipaddr-or-hostname":IpaddrOrHostname(),
    "existing-directory":existing_directory,
    "existing-path":     existing_path,
    "existing-file":     existing_file,
    "existing-dirpath":  existing_dirpath,
    "constructor":       constructor_conversion,
    "key-value":         space_sep_key_value_conversion,
    "byte-size":         SuffixMultiplier({'kb': 1024,
                                           'mb': 1024*1024,
                                           'gb': 1024*1024*1024L,
                                           }),
    "time-interval":     SuffixMultiplier({'s': 1,
                                           'm': 60,
                                           'h': 60*60,
                                           'd': 60*60*24,
                                           }),
    }

class Registry:
    __metatype__ = type
    __slots__ = '_stock', '_other'

    def __init__(self, stock=None):
        if stock is None:
            stock = stock_datatypes.copy()
        self._stock = stock
        self._other = {}

    def get(self, name):
        t = self._stock.get(name)
        if t is None:
            t = self._other.get(name)
            if t is None:
                t = self.search(name)
        return t

    def register(self, name, conversion):
        if self._stock.has_key(name):
            raise ValueError("datatype name conflicts with built-in type: "
                             + `name`)
        if self._other.has_key(name):
            raise ValueError("datatype name already registered:" + `name`)
        self._other[name] = conversion

    def search(self, name):
        if not "." in name:
            raise ValueError("unloadable datatype name: " + `name`)
        components = name.split('.')
        start = components[0]
        g = globals()
        package = __import__(start, g, g)
        modulenames = [start]
        for component in components[1:]:
            modulenames.append(component)
            try:
                package = getattr(package, component)
            except AttributeError:
                n = '.'.join(modulenames)
                package = __import__(n, g, g, component)
        self._other[name] = package
        return package
