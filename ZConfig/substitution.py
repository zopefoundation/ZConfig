##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""Substitution support for ZConfig values."""

import ZConfig

from functions import resolveFunction


def substitute(s, mapping):
    """Interpolate variables from `mapping` into `s`."""
    if "$" in s:
        result = ''
        rest = s
        while rest:
            p, name, namecase, rest = _split(rest)
            result += p
            if name:
                if isinstance(name, _Function):
                    v, rest = name(mapping)
                else:
                    v = mapping.get(name)
                if v is None:
                    raise ZConfig.SubstitutionReplacementError(s, namecase)
                result += v
        return result
    else:
        return s


def isname(s):
    """Return True iff s is a valid substitution name."""
    m = _name_match(s)
    if m:
        return m.group() == s
    else:
        return False


def _split(s):
    # Return a four tuple:  prefix, name, namecase, suffix
    # - prefix is text that can be used literally in the result (may be '')
    # - name is a referenced name, or None
    # - namecase is the name with case preserved
    # - suffix is trailling text that may contain additional references
    #   (may be '' or None)
    if "$" in s:
        i = s.find("$")
        c = s[i+1:i+2]
        if c == "":
            raise ZConfig.SubstitutionSyntaxError(
                "illegal lone '$' at end of source")
        if c == "$":
            return s[:i+1], None, None, s[i+2:]
        prefix = s[:i]
        if c == "{":
            m = _name_match(s, i + 2)
            if not m:
                raise ZConfig.SubstitutionSyntaxError(
                    "'${' not followed by name")
            name = m.group(0)
            i = m.end() + 1
            if not s.startswith("}", i - 1):
                raise ZConfig.SubstitutionSyntaxError(
                    "'${%s' not followed by '}'" % name)
        elif c == "(":
            m = _name_match(s, i + 2)
            if not m:
                raise ZConfig.SubstitutionSyntaxError(
                    "'$(' not followed by name")
            name = m.group(0)
            i = m.end() + 1
            return prefix, _Function(s, m), None, None
        else:
            m = _name_match(s, i+1)
            if not m:
                raise ZConfig.SubstitutionSyntaxError(
                    "'$' not followed by '$' or name")
            name = m.group(0)
            i = m.end()
        return prefix, name.lower(), name, s[i:]
    else:
        return s, None, None, None


import re
_name_match = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*").match
del re


class _Function:
    '''encapsulates a function call substitution.

    A function call has the syntax '$(name args)'
    where *args* is an optionally empty sequence of arguments.
    Argumens in *args* are comma separated.
    Comma can be escaped by duplication.
    Arguments are 'stripped' and then substitution is applied
    to them.

    Note: We currently do not allow parenthesis (neither open nor closed)
      in arguments. Use a definition, should you need such characters
      in your arguments.
    '''
    def __init__(self, s, match):
        '''function instance for function identified by *match* object in string *s*.'''
        name = s[match.start():match.end()]
        f = resolveFunction(name)
        if f is None:
            raise ZConfig.SubstitutionUnknownFunctionError(s, name)
        self._function = f
        # parse arguments
        i = match.end()
        self._args = args = []
        if i >= len(s):
            raise  ZConfig.SubstitutionSyntaxError("'$(%s' is not closed" % name)
        if s[i] == ')':
            self._rest = s[i+1:]
            return
        if not s[i].isspace():
            raise ZConfig.SubstitutionSyntaxError("'$(%s' not followed by either ')' or whitespace" % name)

        i += 1; arg = ''
        while i < len(s):
            c = s[i]; i += 1
            if c in '(': # forbidden characters
                raise  ZConfig.SubstitutionSyntaxError("'$(%s' contains forbidden character '%c'" % (name, c))
            if c not in ',)':
                arg += c; continue
            if c == ',':
                if i < len(s) and s[i] == c: # excaped
                    arg += c; i += 1
                    continue
            args.append(arg.strip()); arg = ''
            if c == ')': # end of function call
                self._rest = s[i:]
                return
        raise  ZConfig.SubstitutionSyntaxError("'$(%s' is not closed" % name)

    def __call__(self, mapping):
        '''call the function.

        Arguments are substitution expanded via *mapping*.

        Returns text for function call and remaining text.
        '''
        args = [substitute(arg, mapping) for arg in self._args]
        v = self._function(mapping, *args)
        return v, self._rest
