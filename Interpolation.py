"""Interpolation support for ZConfig values.

XXX document syntax here
"""

class InterpolationError(Exception):
    """Base exception for string interpolation errors."""

class InterpolationSyntaxError(InterpolationError):
    """Raised when interpolation source text contains syntactical errors."""

    def __init__(self, msg, context):
        self.message = msg
        if context is None:
            self.context = context
        else:
            self.context = context[:]
        InterpolationError.__init__(self, msg, self.context)

class InterpolationRecursionError(InterpolationError):
    """Raised when a nested interpolation is recursive."""

    def __init__(self, name, context):
        self.name = name
        self.context = context[:]
        self.message = ("recursion on %s; current context:\n%s"
                        % (repr(name), ", ".join(context)))
        InterpolationError.__init__(self, name, self.context)


def get(section, name, default=None):
    # XXX should this interpolate from default if that's what's used?
    missing = []
    s = section.get(name, missing)
    if s is missing:
        return default
    if "$" in s:
        accum = []
        _interp(accum, s, section, [name])
        s = ''.join(accum)
    return s


def interpolate(s, section):
    """Interpolate variables from `section` into `s`."""
    if '$' in s:
        accum = []
        _interp(accum, s, section, None)
        s = ''.join(accum)
    return s


def _interp(accum, rest, section, context):
    while 1:
        i = rest.find("$")
        if i < 0:
            accum.append(rest)
            break
        accum.append(rest[:i])
        rest = rest[i+1:]
        if not rest:
            raise InterpolationSyntaxError("lone '$' at end of text", context)
        if rest[0] == "$":
            accum.append("$")
            rest = rest[1:]
        elif rest[0] == "{":
            rest = rest[1:]
            m = _name_match(rest[:])
            if not m:
                raise InterpolationSyntaxError("'${' not followed by name",
                                               context)
            name = m.group(0)
            length = len(name)
            if rest[length:length+1] != "}":
                raise InterpolationSyntaxError(
                    "'${%s' not followed by '}'" % name, context)
            v = section.get(name, "")
            if "$" in v and context:
                if name in context:
                    raise InterpolationRecursionError(name, context)
                _interp(accum, v, section, context + [name])
            else:
                accum.append(v)
            rest = rest[length+1:]
        else:
            m = _name_match(rest)
            if not m:
                raise InterpolationSyntaxError("'$' not followed by name",
                                               context)
            name = m.group(0)
            v = section.get(name, "")
            if "$" in v and context:
                if name in context:
                    raise InterpolationRecursionError(name, context)
                _interp(accum, v, section, context + [name])
            else:
                accum.append(v)
            rest = rest[len(name):]


import re
_name_match = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*").match
del re
