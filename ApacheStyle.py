"""Configuration parser."""

import urlparse

from Common import *


def Parse(resource, context, section):
    lineno = 0
    stack = []
    while 1:
        line = resource.file.readline()
        if not line:
            break
        lineno += 1
        line = line.strip()
        if not line:
            # blank line
            continue
        if line[0] == "#":
            # comment
            continue

        if line[:2] == "</":
            # section end
            if line[-1] != ">":
                raise ConfigurationSyntaxError(
                    "malformed section end", resource.url, lineno)
            if not stack:
                raise ConfigurationSyntaxError(
                    "unexpected section end", resource.url, lineno)
            type = line[2:-1].rstrip()
            if type.lower() != section.type:
                raise ConfigurationSyntaxError(
                    "unbalanced section end", resource.url, lineno)
            try:
                section.finish()
            except ConfigurationError, e:
                raise ConfigurationSyntaxError(e[0], resource.url, lineno)
            section = stack.pop()
            continue

        if line[0] == "<":
            # section start
            if line[-1] != ">":
                raise ConfigurationSyntaxError(
                    "malformed section start", resource.url, lineno)
            isempty = line[-2] == "/"
            if isempty:
                text = line[1:-2].rstrip()
            else:
                text = line[1:-1].rstrip()
            # parse section start stuff here
            m = _section_start_rx.match(text)
            if not m:
                raise ConfigurationSyntaxError(
                    "malformed section header", resource.url, lineno)
            type, name, delegatename = m.group('type', 'name', 'delegatename')
            try:
                newsect = context.nestSection(section, type, name,
                                              delegatename)
            except ConfigurationError, e:
                raise ConfigurationSyntaxError(e[0], resource.url, lineno)
            if not isempty:
                stack.append(section)
                section = newsect
            continue

        if line[0] == "%":
            # directive: import, include
            m = _keyvalue_rx.match(line, 1)
            if not m:
                raise ConfigurationSyntaxError(
                    "missing or unrecognized directive", resource.url, lineno)
            name, arg = m.group('key', 'value')
            if name not in ("define", "import", "include"):
                raise ConfigurationSyntaxError(
                    "unknown directive: " + `name`, resource.url, lineno)
            if not arg:
                raise ConfigurationSyntaxError(
                    "missing argument to %%%s directive" % name,
                    resource.url, lineno)
            if name == "import":
                if stack:
                    raise ConfigurationSyntaxError(
                        "import only allowed at outermost level of a resource",
                        resource.url, lineno)
                newurl = urlparse.urljoin(resource.url, arg)
                context.importConfiguration(section, newurl)
            elif name == "include":
                newurl = urlparse.urljoin(resource.url, arg)
                context.includeConfiguration(section, newurl)
            elif name == "define":
                parts = arg.split(None, 1)
                defname = parts[0]
                defvalue = ''
                if len(parts) == 2:
                    defvalue = parts[1]
                try:
                    resource.define(defname, defvalue)
                except ConfigurationError, e:
                    raise ConfigurationSyntaxError(e[0], resource.url, lineno)
            else:
                assert 0, "unexpected directive for " + `line`
            continue

        # key-value
        m = _keyvalue_rx.match(line)
        if not m:
            raise ConfigurationSyntaxError(
                "malformed configuration data", resource.url, lineno)
        key, value = m.group('key', 'value')
        if not value:
            value = ''
        else:
            value = resource.substitute(value)
        try:
            section.addValue(key, value)
        except ConfigurationError, e:
            raise ConfigurationSyntaxError(e[0], resource.url, lineno)

    if stack:
        raise ConfigurationSyntaxError(
            "unclosed sections no allowed", resource.url, lineno + 1)


import re
# _name_re cannot allow "(" or ")" since we need to be able to tell if
# a section has a name or not: <section (name)> would be ambiguous if
# parentheses were allowed in names.
_name_re = r"[^\s()]+"
_keyvalue_rx = re.compile(r"(?P<key>%s)\s*(?P<value>[^\s].*)?$"
                          % _name_re)
_section_start_rx = re.compile(r"(?P<type>%s)"
                               r"(?:\s+(?P<name>%s))?"
                               r"(?:\s*[(](?P<delegatename>%s)[)])?"
                               r"$"
                               % (_name_re, _name_re, _name_re))
del re
