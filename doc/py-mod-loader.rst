=============================================
 ZConfig.loader --- Resource loading support
=============================================

.. py:module:: ZConfig.loader
  :synopsis: Support classes for resource loading

This module provides some helper classes used by the primary APIs
exported by the :mod:`ZConfig` package.  These classes may be useful
for some applications, especially applications that want to use a
non-default data type registry.

.. py:class:: Resource(file, url, [,fragment])

  Object that allows an open file object and a URL to be bound
  together to ease handling.  Instances have the attributes
  :attr:`file`, :attr:`url`, and :attr:`fragment` which store the
  constructor arguments.  These objects also have a :meth:`close`
  method which will call :meth:`~file.close` on *file*, then set the
  :attr:`file` attribute to ``None`` and the :attr:`closed` attribute to
  ``True``.


.. py:class:: BaseLoader

  Base class for loader objects.  This should not be instantiated
  directly, as the :meth:`loadResource` method must be overridden
  for the instance to be used via the public API.



.. py:class:: ConfigLoader(schema)

  Loader for configuration files.  Each configuration file must
  conform to the schema *schema*.  The ``load*()`` methods
  return a tuple consisting of the configuration object and a
  composite handler.




.. py:class::  SchemaLoader(registry=None)

  Loader that loads schema instances.  All schema loaded by a
  :class:`SchemaLoader` will use the same data type registry.  If
  *registry* is provided and not ``None``, it will be used,
  otherwise an instance of :class:`ZConfig.datatypes.Registry` will be
  used.



Loader Objects
==============

Loader objects provide a general public interface, an interface which
subclasses must implement, and some utility methods.

The following methods provide the public interface:

.. py:method:: BaseLoader.loadURL(url)

  Open and load a resource specified by the URL *url*.
  This method uses the :meth:`loadResource` method to perform the
  actual load, and returns whatever that method returns.


.. py:method:: BaseLoader.loadFile(file, url=None)

  Load from an open file object, *file*.  If given and not
  ``None``, *url* should be the URL of the resource represented
  by *file*.  If omitted or *None*, the ``name``
  attribute of *file* is used to compute a ``file:`` URL, if
  present.

  This method uses the :meth:`loadResource` method to perform the
  actual load, and returns whatever that method returns.


The following method must be overridden by subclasses:

.. py:method:: BaseLoader.loadResource(resource)

  Subclasses of :class:`BaseLoader` must implement this method to
  actually load the resource and return the appropriate
  application-level object.



The following methods can be used as utilities:

.. py:method:: BaseLoader.isPath(s)

  Return true if *s* should be considered a filesystem path rather
  than a URL.


.. py:method:: BaseLoader.normalizeURL(url-or-path)

  Return a URL for *url-or-path*.  If *url-or-path* refers to
  an existing file, the corresponding ``file:`` URL is returned.
  Otherwise *url-or-path* is checked for sanity: if it
  does not have a schema, :exc:`ValueError` is raised, and if it
  does have a fragment identifier, :exc:`~.ConfigurationError` is
  raised.

  This uses :meth:`isPath` to determine whether *url-or-path*
  is a URL of a filesystem path.


.. py:method:: BaseLoader.openResource(url)

  Returns a resource object that represents the URL *url*.  The
  URL is opened using the :func:`urllib2.urlopen` function, and
  the returned resource object is created using
  :meth:`createResource`.  If the URL cannot be opened,
  exc`ConfigurationError` is raised.


.. py:method:: BaseLoader.createResource(file, url)

  Returns a resource object for an open file and URL, given as
  *file* and *url*, respectively.  This may be overridden by a
  subclass if an alternate resource implementation is desired.
