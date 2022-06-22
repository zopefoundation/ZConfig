
.. _documenting-components:

========================
 Documenting Components
========================

ZConfig includes a docutils directive for documenting components and
schemas that you create. This directive can function as a Sphinx
extension if you include ``ZConfig.sphinx`` in the ``extensions``
value of your Sphinx configuration:

.. code-block:: python

  extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.interpsphinx',
    'ZConfig.sphinx',
  ]

There is one directive:

.. rst:directive:: .. zconfig:: <package-name>

   .. versionadded:: 3.2.0

   Document the components or schema found in the Python package *package-name*.

   By default, the contents of ``component.xml`` will be documented.
   You can specify the ``:file:`` option to choose a different file
   from that package. This file can refer to a schema or component
   definition.

   Each component will have its name, type, and default value
   documented. The description of the component will be rendered as
   reStructuredText (and so can use directives like ``py:class:`` and
   ``py:meth:`` to perform cross references). Any example for the
   component will be rendered as a pre-formatted block.

   All ZConfig components reachable will be documented, in the order
   in which they are found. Often times, if your component extends
   other components, this will produce too much documentation (it will
   document the components you are extending in addition to the unique
   aspects of your component). You can use the ``:members:`` and
   ``:excluded-members:`` options to limit this.

   Both of these options take a space-separated list of component
   names. These options can be used together. When ``:members:`` is
   given, only items that are explicitly named, or that are reachable
   from such items, are documented. The ``:excluded-members:`` option
   overrides this, causing any such members to be explicitly excluded.

   These options are also useful for breaking the description of a
   component up into multiple distinct sections, with narrative
   documentation between them. For example, to document the main
   logger component provided by ZConfig separately from each type of
   handler ZConfig provides, the document might look like this:

.. code-block:: rst

   You can configure a logger and logging level with ZConfig:

   .. zconfig:: ZConfig.components.logger
       :members: ZConfig.logger.base-logger
       :excluded-members: zconfig.logger.handler

   ZConfig supports multiple different types of handlers for a given logger:

   .. zconfig:: ZConfig.components.logger
       :members: zconfig.logger.handler
