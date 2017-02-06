.. _standard-datatypes:

============================
 Standard ZConfig Datatypes
============================

There are a number of data types which can be identified using the
``datatype``  attribute on ``key`` ,
``sectiontype``, and ``schema`` elements.
Applications may extend the set of datatypes by calling the
:meth:`~.register` method of the data type registry being used or by
using Python dotted-names to refer to conversion routines defined in
code.

The following data types are provided by the default type registry.


**basic-key**
  The default data type for a key in a ZConfig configuration file.
  The result of conversion is always lower-case, and matches the
  regular expression ``[a-z][-._a-z0-9]*``.

**boolean**
  Convert a human-friendly string to a boolean value.  The names
  ``yes``, ``on``, and ``true`` convert to ``True``,
  while ``no``, ``off``, and ``false`` convert to
  ``False``.  Comparisons are case-insensitive.  All other
  input strings are disallowed.

**byte-size**
  A specification of a size, with byte multiplier suffixes (for
  example, ``128MB``).  Suffixes are case insensitive and may be
  ``KB``, ``MB``, or ``GB``

**dotted-name**
  A string consisting of one or more **identifier** values
  separated by periods (``.``).

**dotted-suffix**
  A string consisting of one or more **identifier** values
  separated by periods (``.``), possibly prefixed by a
  period.  This can be used to indicate a dotted name that may be
  specified relative to some base dotted name.

**existing-dirpath**
  Validates that the directory portion of a pathname exists.  For
  example, if the value provided is '/foo/bar', '/foo' must
  be an existing directory.  No conversion is performed.

**existing-directory**
  Validates that a directory by the given name exists on
  the local filesystem.  No conversion is performed.

**existing-file**
  Validates that a file by the given name exists.  No conversion
  is performed.

**existing-path**
  Validates that a path (file, directory, or symlink) by the
  given name exists on the local filesystem.  No conversion
  is performed.

**float**
  A Python float.  ``Inf``, ``-Inf``, and ``NaN`` are not
  allowed.

**identifier**
  Any valid Python identifier.

**inet-address**
  An Internet address expressed as a ``(hostname,
  port)`` pair.  If only the port is specified, the default host
  will be returned for *hostname*.  The default host is
  ``localhost`` on Windows and the empty string on all other
  platforms.  If the port is omitted, ``None`` will be returned for
  *port*. IPv6 addresses can be specified in colon-separated notation;
  if both host and port need to be specified, the bracketed form
  (``[addr]:port``) must be used.

**inet-binding-address**
  An Internet address expressed as a ``(hostname,
  port)`` pair.  The address is suitable for binding a socket.
  If only the port is specified, the default host will be returned for
  *hostname*.  The default host is the empty string on all
  platforms.  If the port is omitted, ``None`` will be returned for
  *port*.

**inet-connection-address**
  An Internet address expressed as a ``(hostname,
  port)`` pair.  The address is suitable for connecting a socket
  to a server.  If only the port is specified, ``'127.0.0.1'`` will
  be returned for *hostname*.  If the port is omitted, ``None``
  will be returned for *port*.

**integer**
  Convert a value to an integer.  This will be a Python :class:`int` if
  the value is in the range allowed by :class`int`, otherwise a Python
  :class:`long` is returned.

**ipaddr-or-hostname**
  Validates a valid IP address or hostname.  If the first
  character is a digit, the value is assumed to be an IP
  address.  If the first character is not a digit, the value
  is assumed to be a hostname.  Strings containing colons are
  considered IPv6 address.  Hostnames are converted to lower
  case.

**locale**
  Any valid locale specifier accepted by the available
  :func:`locale.setlocale` function.  Be aware that only the
  ``'C'`` locale is supported on some platforms.

**null**
  No conversion is performed; the value passed in is the value
  returned.  This is the default data type for section values.

**port-number**
  Returns a valid port number as an integer.  Validity does not imply
  that any particular use may be made of the port, however.  For
  example, port number lower than 1024 generally cannot be bound by
  non-root users.

**socket-address**
  An address for a socket.  The converted value is an object providing
  two attributes.  ``family`` specifies the address family
  (:data:`socket.AF_INET` or :data:`socket.AF_UNIX`), with ``None`` instead
  of ``AF_UNIX`` on platforms that don't support it.  The
  ``address`` attribute will be the address that should be passed
  to the socket's :meth:`~socket.socket.bind` method.  If the family is
  ``AF_UNIX``, the specific address will be a pathname; if the
  family is ``AF_INET``, the second part will be the result of
  the **inet-address** conversion.

**string**
  Returns the input value as a string.  If the source is a Unicode
  string, this implies that it will be checked to be simple 7-bit
  ASCII.  This is the default data type for values in
  configuration files.

**time-interval**
  A specification of a time interval in seconds, with multiplier
  suffixes (for example, ``12h``).  Suffixes are case insensitive
  and may be ``s`` (seconds), ``m`` (minutes), ``h`` (hours),
  or ``d`` (days).

**timedelta**
  Similar to the **time-interval**, this data type returns a Python
  :class:`datetime.timedelta` object instead of a float.  The set of suffixes
  recognized by **timedelta** are: ``w`` (weeks), ``d`` (days),
  ``h`` (hours), ``m`` (minutes), ``s`` (seconds).  Values may be
  floats, for example: ``4w 2.5d 7h 12m 0.001s``.
