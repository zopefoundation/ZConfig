"""Top-level configuration handle."""

import os
import urllib
import urllib2
import urlparse

from Common import *
from Config import Configuration, ImportingConfiguration


class Context:

    def __init__(self):
        #Configuration.__init__(self, None, None, url)
        self._imports = []         # URL  -> Configuration
        self._named_sections = {}  # name -> Configuration
        self._needed_names = {}    # name -> [needy Configuration, ...]
        self._current_imports = []

    # subclass-support API

    def createImportedSection(self, section, url):
        return ImportingConfiguration(None, None, url)

    def createNestedSection(self, section, type, name, delegatename):
        if name:
            name = name.lower()
        return Configuration(type.lower(), name, section.url)

    def createToplevelSection(self, url):
        return ImportingConfiguration(None, None, url)

    def getDelegateType(self, type):
        # Applications must provide delegation typing information by
        # overriding the Context.getDelegateType() method.
        return type.lower()

    def parse(self, file, section, url):
        from ApacheStyle import Parse
        Parse(file, self, section, url)

    # public API

    def load(self, url):
        """Load a resource from a URL or pathname."""
        if os.path.exists(url):
            url = "file://" + urllib.pathname2url(os.path.abspath(url))
        top = self.createToplevelSection(url)
        self._imports = [top]
        self._parse_url(url, top)
        self._finish()
        return top

    # interface for parser

    def importConfiguration(self, section, url):
        for config in self._imports:
            if config.url == url:
                return config
        newsect = self.createImportedSection(section, url)
        self._imports.append(newsect)
        section.addImport(newsect)
        self._parse_url(url, newsect)

    def includeConfiguration(self, section, url):
        # XXX we always re-parse, unlike import
        file = urllib2.urlopen(url)
        try:
            self.parse(file, section, url)
        finally:
            file.close()

    def nestSection(self, section, type, name, delegatename):
        if name:
            name = name.lower()
        type = type.lower()
        if name and self._named_sections.has_key(name):
            # Make sure sections of the same name are not defined
            # twice in the same resource, and that once a name has
            # been defined, its type is not changed by a section from
            # another resource.
            oldsect = self._named_sections[name]
            if oldsect.url == section.url:
                raise ConfigurationError(
                    "named section cannot be defined twice in same resource")
            if oldsect.type != type:
                raise ConfigurationError(
                    "named section cannot change type")
        newsect = self.createNestedSection(section, type, name, delegatename)
        if delegatename:
            # The knitting together of the delegation graph needs this.
            try:
                L = self._needed_names[delegatename]
            except KeyError:
                L = []
                self._needed_names[delegatename] = L
            L.append(newsect)
        section.addChildSection(newsect)
        if name:
            self._named_sections[name] = newsect
            current = self._current_imports[-1]
            if section is not current:
                current.addNamedSection(newsect)
            for config in self._current_imports[:-1]:
                # XXX seems very painful
                if not config._sections_by_name.has_key((type, name)):
                    config.addNamedSection(newsect)
        return newsect

    # internal helpers

    def _parse_url(self, url, section):
        if urlparse.urlparse(url)[-1]:
            raise ConfigurationError(
                "fragment identifiers are not currently supported")
        file = urllib2.urlopen(url)
        self._current_imports.append(section)
        try:
            self.parse(file, section, url)
        finally:
            del self._current_imports[-1]
            file.close()

    def _finish(self):
        # Resolve section delegations
        for name, L in self._needed_names.items():
            section = self._named_sections[name]
            for referrer in L:
                type = self.getDelegateType(referrer.type)
                if type is None:
                    raise ConfigurationTypeError(
                        "%s sections are not allowed to specify delegation\n"
                        "(in %s)"
                        % (repr(referrer.type), referrer.url),
                        referrer.type, None)
                type = type.lower()
                if type != section.type:
                    raise ConfigurationTypeError(
                        "%s sections can only inherit from %s sections\n"
                        "(in %s)"
                        % (repr(referrer.type), repr(type), referrer.url),
                        referrer.type, type)
                referrer.setDelegate(section)
        self._needed_names = None
