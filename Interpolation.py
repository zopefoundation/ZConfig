"""Interpolation support for ZConfig values.

XXX document syntax here
"""


class InterpolationSyntaxError(Exception):
    """Raised when interpolation source text contains syntactical errors."""
    pass


def interpolate(s, section):
    """Interpolate variables from `section` into `s`."""
    if '$' in s:
        accum = []
        _interp(accum, s, section)
        return ''.join(accum)
    else:
        return s


def _interp(accum, rest, section):
    while 1:
        i = rest.find("$")
        if i < 0:
            accum.append(rest)
            break
        accum.append(rest[:i])
        rest = rest[i+1:]
        if not rest:
            raise InterpolationSyntaxError("lone '$' at end of text")
        if rest[0] == "$":
            accum.append("$")
            rest = rest[1:]
        elif rest[0] == "{":
            rest = rest[1:]
            m = _name_match(rest[:])
            if not m:
                raise InterpolationSyntaxError("'${' not followed by name")
            name = m.group(0)
            length = len(name)
            if rest[length:length+1] != "}":
                raise InterpolationSyntaxError("'${%s' not followed by '}'"
                                               % name)
            accum.append(section.get(name, ""))
            rest = rest[length+1:]
        else:
            m = _name_match(rest)
            if not m:
                raise InterpolationSyntaxError("'$' not followed by name")
            name = m.group(0)
            accum.append(section.get(name, ""))
            rest = rest[len(name):]


import re
_name_match = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*").match
del re
