=========================================
 ZConfig --- Basic configuration support
=========================================

.. py:module:: ZConfig
   :synopsis: Configuration package.


Functions
=========

The main :mod:`ZConfig` package exports these convenience functions:

.. autofunction:: loadConfig

.. autofunction:: loadConfigFile

.. autofunction:: loadSchema

.. autofunction:: loadSchemaFile


Exceptions
==========

The following exceptions are defined by this package:

.. autoexception:: ConfigurationError()
   :show-inheritance:


.. autoexception:: ConfigurationSyntaxError()


.. autoexception:: DataConversionError()
   :show-inheritance:


.. autoexception:: SchemaError()


.. autoexception:: SchemaResourceError()
   :show-inheritance:

.. autoexception:: SubstitutionReplacementError()
   :show-inheritance:

.. autoexception:: SubstitutionSyntaxError()



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
