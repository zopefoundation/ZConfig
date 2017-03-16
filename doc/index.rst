.. ZConfig documentation master file, created by
   sphinx-quickstart on Thu Jan 12 14:36:41 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

============================
 Configuration With ZConfig
============================

ZConfig is a Python library for creating extensible configuration
documents (files). The configuration documents are written in a syntax
reminiscent of that used by the Apache HTTP Server, while the configuration
mechanism is itself configured using a schema specification written
in XML.

ZConfig is used by projects such as the Zope application server and
ZODB, and is easily used by other projects. ZConfig only relies on the
Python standard library.

For information on reading and writing configuration documents, see
:doc:`using-zconfig`. For the extremely common usage of configuring
the Python :mod:`logging` framework, see :doc:`using-logging`.

For information on using ZConfig to create custom configurations for
you projects, see :doc:`developing-with-zconfig`.

Development of ZConfig is hosted on `GitHub <https://github.com/zopefoundation/ZConfig>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   using-zconfig
   using-logging
   developing-with-zconfig
   zconfig
   tools

.. toctree::
   :maxdepth: 1

   changelog


====================
 Indices and tables
====================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
