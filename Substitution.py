"""Substitution support for ZConfig values."""

class SubstitutionError(Exception):
    """Base exception for string substitution errors."""

    def __init__(self, msg, context):
        self.message = msg
        self.context = context

    def __str__(self):
        return self.message

class SubstitutionSyntaxError(SubstitutionError):
    """Raised when interpolation source text contains syntactical errors."""

    def __init__(self, msg, context):
        if context is not None:
            context = context[:]
        SubstitutionError.__init__(self, msg, context)

class SubstitutionRecursionError(SubstitutionError):
    """Raised when a nested interpolation is recursive."""

    def __init__(self, name, context):
        self.name = name
        msg = ("recursion on %s; current context:\n%s"
               % (repr(name), ", ".join(context)))
        SubstitutionError.__init__(self, msg, context[:])


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


def substitute(s, section):
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
            accum.append("$")
            break
        if rest[0] == "$":
            accum.append("$")
            rest = rest[1:]
        elif rest[0] == "{":
            rest = rest[1:]
            m = _name_match(rest[:])
            if not m:
                raise SubstitutionSyntaxError("'${' not followed by name",
                                              context)
            name = m.group(0)
            length = len(name)
            if rest[length:length+1] != "}":
                raise SubstitutionSyntaxError(
                    "'${%s' not followed by '}'" % name, context)
            v = section.get(name)
            if v is None:
                parent = getattr(section, "container", None)
                while parent is not None:
                    v = parent.get(name)
                    if v is not None:
                        break
                    parent = getattr(parent, "container", None)
                else:
                    v = ""
            if "$" in v and context:
                if name in context:
                    raise SubstitutionRecursionError(name, context)
                _interp(accum, v, section, context + [name])
            else:
                accum.append(v)
            rest = rest[length+1:]
        else:
            m = _name_match(rest)
            if not m:
                accum.append("$")
                continue
            name = m.group(0)
            v = section.get(name, "")
            if "$" in v and context:
                if name in context:
                    raise SubstitutionRecursionError(name, context)
                _interp(accum, v, section, context + [name])
            else:
                accum.append(v)
            rest = rest[len(name):]


import re
_name_match = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*").match
del re
