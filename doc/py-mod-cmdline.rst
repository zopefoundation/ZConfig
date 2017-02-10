===================================================
 ZConfig.cmdline --- Command-line override support
===================================================

.. automodule:: ZConfig.cmdline

.. autoclass:: ExtendedConfigLoader(schema)
   :show-inheritance:

The following additional method is provided, and is the only way to
provide position information to associate with command-line
parameters:

.. automethod:: ExtendedConfigLoader.addOption
