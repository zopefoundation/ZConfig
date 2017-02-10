=============================================
 ZConfig.loader --- Resource loading support
=============================================

.. py:module:: ZConfig.loader
  :synopsis: Support classes for resource loading

This module provides some helper classes used by the primary APIs
exported by the :mod:`ZConfig` package.  These classes may be useful
for some applications, especially applications that want to use a
non-default data type registry.

.. autoclass:: Resource


.. autoclass:: ConfigLoader
   :show-inheritance:


.. autoclass:: SchemaLoader
   :show-inheritance:


Loader Objects
==============

Loader objects provide a general public interface, an interface which
subclasses must implement, and some utility methods.

.. autoclass:: BaseLoader


The following methods provide the public interface:

.. automethod:: BaseLoader.loadURL


.. automethod:: BaseLoader.loadFile


The following method must be overridden by subclasses:

.. automethod:: BaseLoader.loadResource


The following methods can be used as utilities:

.. automethod:: BaseLoader.isPath

.. automethod:: BaseLoader.normalizeURL

.. automethod:: BaseLoader.openResource

.. automethod:: BaseLoader.createResource
