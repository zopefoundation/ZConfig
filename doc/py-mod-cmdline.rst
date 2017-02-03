===================================================
 ZConfig.cmdline --- Command-line override support
===================================================

.. py:module:: ZConfig.cmdline
   :synopsis: Support for command-line overrides for configuration settings.

This module exports an extended version of the :class:`ZConfig.loader.ConfigLoader`
class from the :mod:`ZConfig.loader` module.  This provides
support for overriding specific settings from the configuration file
from the command line, without requiring the application to provide
specific options for everything the configuration file can include.

.. py:class:: ExtendedConfigLoader(schema)

  Construct a :class:`ConfigLoader` subclass that adds support for
  command-line overrides.


The following additional method is provided, and is the only way to
provide position information to associate with command-line
parameters:

.. py:method:: ExtendedConfigLoader.addOption(spec [, pos])

  Add a single value to the list of overridden values.  The *spec*
  argument is a value specified, as described for the
  :func:`ZConfig.loadConfig` function.  A source
  position for the specifier may be given as *pos*.  If *pos*
  is specified and not ``None``, it must be a sequence of three
  values.  The first is the URL of the source (or some other
  identifying string).  The second and third are the line number and
  column of the setting.  These position information is only used to
  construct a :exc:`~.DataConversionError` when data conversion
  fails.
