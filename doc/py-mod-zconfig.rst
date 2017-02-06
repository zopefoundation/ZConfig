=========================================
 ZConfig --- Basic configuration support
=========================================

.. py:module:: ZConfig
   :synopsis: Configuration package.


The main :mod:`ZConfig` package exports these convenience functions:

.. py:function:: loadConfig(schema, url, [overrides])

  Load and return a configuration from a URL or pathname given by
  *url*.  *url* may be a URL, absolute pathname, or relative
  pathname.  Fragment identifiers are not supported.  *schema* is
  a reference to a schema loaded by :func:`loadSchema` or
  :func:`loadSchemaFile`.

  The return value is a tuple containing the configuration object and
  a composite handler that, when called with a name-to-handler
  mapping, calls all the handlers for the configuration.

  The optional *overrides* argument represents information derived
  from command-line arguments.  If given, it must be either a sequence
  of value specifiers, or ``None``.  A "value specifier" is a
  string of the form ``optionpath=value``.  The
  *optionpath* specifies the "full path" to the configuration
  setting: it can contain a sequence of names, separated by
  ``/`` characters. Each name before the last names a section
  from the configuration file, and the last name corresponds to a key
  within the section identified by the leading section names.  If
  *optionpath* contains only one name, it identifies a key in the
  top-level schema.  *value* is a string that will be treated
  just like a value in the configuration file.


.. py:function:: loadConfigFile(schema, file, [url, overrides])

  Load and return a configuration from an opened file object.  If
  *url* is omitted, one will be computed based on the
  ``name`` attribute of *file*, if it exists.  If no URL can
  be determined, all ``%include`` statements in the
  configuration must use absolute URLs.  *schema* is a reference
  to a schema loaded by :func:`loadSchema` or
  :func:`loadSchemaFile`.

  The return value is a tuple containing the configuration object and
  a composite handler that, when called with a name-to-handler
  mapping, calls all the handlers for the configuration.
  The *overrides* argument is the same as for the
  :func:`loadConfig` function.


.. py:function:: loadSchema(url)

  Load a schema definition from the URL *url*.
  *url* may be a URL, absolute pathname, or relative pathname.
  Fragment identifiers are not supported.

  The resulting
  schema object can be passed to :func:`loadConfig` or
  :func:`loadConfigFile`.  The schema object may be used as many
  times as needed.


.. py:function:: loadSchemaFile(file, [url])

  Load a schema definition from the open file object *file*.  If
  *url* is given and not ``None``, it should be the URL of
  resource represented by *file*.  If *url* is omitted or
  ``None``, a URL may be computed from the ``name`` attribute
  of *file*, if present.  The resulting schema object can
  be passed to :func:`loadConfig` or :func:`loadConfigFile`.
  The schema object may be used as many times as needed.


The following exceptions are defined by this package:

.. py:exception:: ConfigurationError

  Base class for exceptions specific to the :mod:`ZConfig` package.
  All instances provide a ``message`` attribute that describes
  the specific error, and a ``url`` attribute that gives the URL
  of the resource the error was located in, or ``None``.


.. py:exception:: ConfigurationSyntaxError

  Exception raised when a configuration source does not conform to the
  allowed syntax.  In addition to the ``message`` and
  ``url`` attributes, exceptions of this type offer the
  ``lineno`` attribute, which provides the line number at which
  the error was detected.


.. py:exception:: DataConversionError

  Raised when a data type conversion fails with
  :exc:`ValueError`.  This exception is a subclass of both
  :exc:`ConfigurationError` and :exc:`ValueError`.  The
  :func:`str` of the exception provides the explanation from the
  original :exc:`ValueError`, and the line number and URL of the
  value which provoked the error.  The following additional attributes
  are provided:


  =============    =============
  Attribute        Value
  =============    =============
  ``colno``        column number at which the value starts, or ``None``
  ``exception``    the original :exc:`ValueError` instance
  ``lineno``       line number on which the value starts
  ``message``      :func:`str` returned by the original :exc:`ValueError`
  ``value``        original value passed to the conversion function
  ``url``          URL of the resource providing the value text
  =============    =============


.. py:exception:: SchemaError

  Raised when a schema contains an error.  This exception type
  provides the attributes ``url``, ``lineno``, and
  ``colno``, which provide the source URL, the line number, and
  the column number at which the error was detected.  These attributes
  may be ``None`` in some cases.


.. py:exception:: SchemaResourceError

  Raised when there's an error locating a resource required by the
  schema.  This is derived from :exc:`SchemaError`.  Instances of
  this exception class add the attributes ``filename``,
  ``package``, and ``path``, which hold the filename
  searched for within the package being loaded, the name of the
  package, and the ``__path__`` attribute of the package itself (or
  ``None`` if it isn't a package or could not be imported).


.. py:exception:: SubstitutionReplacementError

  Raised when the source text contains references to names which are
  not defined in *mapping*.  The attributes ``source`` and
  ``name`` provide the complete source text and the name
  (converted to lower case) for which no replacement is defined.


.. py:exception:: SubstitutionSyntaxError

  Raised when the source text contains syntactical errors.

.. _basic-usage:

Basic Usage
===========

The simplest use of :mod:`ZConfig` is to load a configuration
based on a schema stored in a file.  This example loads a
configuration file specified on the command line using a schema in the
same directory as the script:

.. code-block:: python


  import os
  import sys
  import ZConfig

  try:
      myfile = __file__
  except NameError:
      myfile = os.path.realpath(sys.argv[0])

  mydir = os.path.dirname(myfile)

  schema = ZConfig.loadSchema(os.path.join(mydir, 'schema.xml'))
  conf, handler = ZConfig.loadConfig(schema, sys.argv[1])


If the schema file contained this schema::


  <schema>
    <key name='server' required='yes'/>
    <key name='attempts' datatype='integer' default='5'/>
  </schema>


and the file specified on the command line contained this text::


  # sample configuration

  server www.example.com

then the configuration object ``conf`` loaded above would have two
attributes, *server* with the value ``'www.example.com'`` and
*attempts* with the value ``5``.
