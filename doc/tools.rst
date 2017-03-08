=================
 ZConfig Tooling
=================

ZConfig ships with some tools that can be helpful to anyone
either writing configurations or writing programs that read
configurations.

Schema and Configuration Validation
===================================

When ZConfig is installed, it installs a program called ``zconfig``
that can validate both schemas and configurations written against
those schemas:

  .. program-output:: zconfig --help

Documenting Schemas
===================

ZConfig also installs a tool called ``zconfig_schema2html`` that can
print schemas in a simple HTML format.

.. hint:: To document components in reStructuredText, e.g., with
		 Sphinx, see :ref:`documenting-components`.

.. program-output:: zconfig_schema2html --help
