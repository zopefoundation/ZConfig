"""Substitution support for ZConfig values."""

class SubstitutionError(Exception):
    """Base exception for string substitution errors."""

    def __init__(self, msg, context):
        self.message = msg
        if context is not None:
            context = context[:]
        self.context = context

    def __str__(self):
        return self.message

class SubstitutionSyntaxError(SubstitutionError):
    """Raised when interpolation source text contains syntactical errors."""

    def __init__(self, msg, context):
        SubstitutionError.__init__(self, msg, context)

class SubstitutionRecursionError(SubstitutionError):
    """Raised when a nested interpolation is recursive."""

    def __init__(self, name, context):
        self.name = name
        msg = ("recursion on %s; current context:\n%s"
               % (repr(name), ", ".join(context)))
        SubstitutionError.__init__(self, msg, context)


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
    if "$" in s:
        accum = []
        _interp(accum, s, section, None)
        s = ''.join(accum)
    return s


def getnames(s):
    """Return a list of names referenced by s."""
    if "$" in s:
        L = []
        while s:
            p, name, s = _split(s, None)
            if name and name not in L:
                L.append(name)
        return L
    else:
        return []


def _interp(accum, rest, section, context):
    while 1:
        s, name, rest = _split(rest, context)
        if s:
            accum.append(s)
        if name:
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
        if not rest:
            return


def _split(s, context):
    # Return a triple:  prefix, name, suffix
    # - prefix is text that can be used literally in the result (may be '')
    # - name is a referenced name, or None
    # - suffix is trailling text that may contain additional references
    #   (may be '' or None)
    if "$" in s:
        i = s.find("$")
        c = s[i+1:i+2]
        if c == "":
            return s, None, None
        if c == "$":
            return s[:i+1], None, s[i+2:]
        prefix = s[:i]
        if c == "{":
            m = _name_match(s, i + 2)
            if not m:
                raise SubstitutionSyntaxError("'${' not followed by name",
                                              context)
            name = m.group(0)
            i = m.end() + 1
            if not s.startswith("}", i - 1):
                raise SubstitutionSyntaxError(
                    "'${%s' not followed by '}'" % name, context)
        else:
            m = _name_match(s, i+1)
            if not m:
                return prefix + "$", None, s[i+1:]
            name = m.group(0)
            i = m.end()
        return prefix, name.lower(), s[i:]
    else:
        return s, None, None


import re
_name_match = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*").match
del re
