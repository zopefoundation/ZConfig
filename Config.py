"""Configuration data structure."""

from Common import *

class Configuration:
    def __init__(self, container, type, name, url):
        self.container = container
        self.type = type
        self.name = name or None
        self.delegate = None
        self.url = url
        self._sections_by_name = {}
        self._sections = []
        self._data = {}

    def __repr__(self):
        klass = self.__class__
        classname = "%s.%s" % (klass.__module__, klass.__name__)
        if self.name:
            return "<%s for %s (type %s) at %#x>" \
                   % (classname, repr(self.name),
                      repr(self.type), id(self))
        elif self.type:
            return "<%s (type %s) at 0x%x>" \
                   % (classname, repr(self.type), id(self))
        else:
            return "<%s at 0x%x>" % (classname, id(self))

    def finish(self):
        pass

    def setDelegate(self, section):
        if self.delegate is not None:
            raise ConfigurationError("cannot modify delegation")
        self.delegate = section

    def addChildSection(self, section):
        """Add a section that is a child of this one."""
        if section.name:
            self.addNamedSection(section)
        elif not section.type:
            raise ValueError("'type' must be specified")
        self._sections.append(section)

    def addNamedSection(self, section):
        """Add a named section that may"""
        name = section.name
        type = section.type
        if not type:
            raise ValueError("'type' must be specified")
        key = type, name
        child = self._sections_by_name.get(key)
        if child is None or child.url != self.url:
            self._sections_by_name[key] = section
        else:
            raise ConfigurationError(
                "cannot replace existing named section")

    def getSection(self, type, name=None):
        # get section by name, relative to this section
        type = type.lower()
        if name:
            return self._sections_by_name[(type, name.lower())]
        else:
            L = []
            for sect in self._sections:
                if sect.type == type:
                    L.append(sect)
            if len(L) > 1:
                raise ConfigurationConflictingSectionError(type, name)
            if L:
                return L[0]
            elif self.delegate:
                return self.delegate.getSection(type)
            else:
                return None

    def getChildSections(self, type=None):
        if type is None:
            return self._sections[:]
        else:
            return [sect for sect in self._sections if sect.type == type]

    def addValue(self, key, value):
        key = key.lower()
        try:
            self._data[key]
        except KeyError:
            self._data[key] = value
        else:
            raise ConfigurationError("cannot add existing key")

    def setValue(self, key, value):
        key = key.lower()
        self._data[key] = value

    def has_key(self, key):
        key = key.lower()
        if self._data.has_key(key):
            return True
        elif self.delegate:
            return self.delegate.has_key(key)
        else:
            return False

    def items(self):
        """Returns a list of key-value pairs for this section.

        The returned list includes pairs retrieved from the delegation chain.
        """
        if self.delegate is None:
            return self._data.items()
        else:
            L = [self._data]
            while self.delegate is not None:
                self = self.delegate
                L.append(self._data)
            d = L.pop().copy()
            L.reverse()
            for m in L:
                d.update(m)
            return d.items()

    def keys(self):
        if self.delegate is None:
            return self._data.keys()
        else:
            L1 = self.delegate.keys()
            L2 = self._data.keys()
            for k in L1:
                if k not in L2:
                    L2.append(k)
            return L2

    def __getitem__(self, key):
        k = key.lower()
        if self._data.has_key(k):
            return self._data[k]
        elif self.delegate:
            v = self.delegate.get(k)
            if v is None:
                raise KeyError(key)
            return v
        else:
            raise KeyError(key)

    def get(self, key, default=None):
        key = key.lower()
        try:
            return self._data[key]
        except KeyError:
            if self.delegate is None:
                return default
            else:
                return self.delegate.get(key, default)

    _boolean_values = {
         'true': True,  'yes': True,   'on': True,
        'false': False,  'no': False, 'off': False,
        } 

    def getbool(self, key, default=None):
        missing = []
        s = self.get(key, missing)
        if s is missing:
            return default
        try:
            return self._boolean_values[s.lower()]
        except KeyError:
            raise ValueError("%s is not a valid boolean value" % repr(s))

    def getfloat(self, key, default=None, min=None, max=None):
        missing = []
        s = self.get(key, missing)
        if s is missing:
            return default
        x = float(self.get(key))
        self._check_range(key, x, min, max)
        return x

    def getint(self, key, default=None, min=None, max=None):
        missing = []
        s = self.get(key, missing)
        if s is missing:
            return default
        x = int(s)
        self._check_range(key, x, min, max)
        return x

    def _check_range(self, key, x, min, max):
        if min is not None and x < min:
            raise ValueError("value for %s must be at least %s, found %s"
                             % (repr(key), min, x))
        if max is not None and x > max:
            raise ValueError("value for %s must be no more than %s, found %s"
                             % (repr(key), max, x))

    def getlist(self, key, default=None):
        missing = []
        s = self.get(key, missing)
        if s is missing:
            return default
        else:
            return s.split()


class ImportingConfiguration(Configuration):
    def __init__(self, url):
        self._imports = []
        Configuration.__init__(self, None, None, None, url)

    def addImport(self, section):
        self._imports.append(section)

    def get(self, key, default=None):
        s = Configuration.get(self, key, default)
        if s is default:
            for config in self._imports:
                s = config.get(key, default)
                if s is not default:
                    break
        return s
