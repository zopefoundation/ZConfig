"""Configuration parser."""

import urlparse

from Common import *


def Parse(file, context, section, url):
    lineno = 0
    stack = []
    while 1:
        line = file.readline()
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
                    "malformed section end", url, lineno)
            if not stack:
                raise ConfigurationSyntaxError(
                    "unexpected section end", url, lineno)
            type = line[2:-1].rstrip()
            if type.lower() != section.type:
                raise ConfigurationSyntaxError(
                    "unbalanced section end", url, lineno)
            section = stack.pop()
            continue
        if line[0] == "<":
            # section start
            if line[-1] != ">":
                raise ConfigurationSyntaxError(
                    "malformed section start", url, lineno)
            isempty = line[-2] == "/"
            if isempty:
                text = line[1:-2].rstrip()
            else:
                text = line[1:-1].rstrip()
            # parse section start stuff here
            m = _section_start_rx.match(text)
            if not m:
                raise ConfigurationSyntaxError(
                    "malformed section header", url, lineno)
            type, name, delegatename = m.group('type', 'name', 'delegatename')
            try:
                newsect = context.nestSection(section, type, name,
                                              delegatename)
            except ConfigurationError, e:
                raise ConfigurationSyntaxError(e[0], url, lineno)
            if not isempty:
                stack.append(section)
                section = newsect
            continue
        # key-value
        m = _keyvalue_rx.match(line)
        if not m:
            raise ConfigurationSyntaxError(
                "malformed configuration data", url, lineno)
        key, value = m.group('key', 'value')
        if key == "import":
            if stack:
                raise ConfigurationSyntaxError(
                    "import only allowed at the outermost level of a resource",
                    url, lineno)
            newurl = urlparse.urljoin(url, value)
            context.importConfiguration(section, newurl)
        elif key == "include":
            newurl = urlparse.urljoin(section.url, value)
            context.includeConfiguration(section, newurl)
        else:
            try:
                section.addValue(key, value)
            except ConfigurationError, e:
                raise ConfigurationSyntaxError(e[0], url, lineno)
    if stack:
        raise ConfigurationSyntaxError(
            "unclosed sections no allowed", url, lineno + 1)


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
