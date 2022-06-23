====================================
 Reading and Writing Configurations
====================================

This document describes how to read and write configurations in the ZConfig
format.

Reading Configurations
======================

For information on using ZConfig configuration documents in Python,
see :mod:`ZConfig` and especially the example at :ref:`basic-usage`.

For information about configuring the :mod:`logging` framework, see
:doc:`using-logging`.

.. _syntax:

Writing Configurations
======================

.. Unless we're talking about the schema, nginx syntax is closest
.. to zconfig (those that use %import won't lex with XML)

.. highlight:: nginx

Like the :mod:`ConfigParser`
format, this format supports key-value pairs arranged in sections.
Unlike the :mod:`ConfigParser` format, sections are typed and can be
organized hierarchically.
Additional files may be included if needed.  Schema components not
specified in the application schema can be imported from the
configuration file.  Though both formats are substantially
line-oriented, this format is more flexible.

The intent of supporting nested section is to allow setting up the
configurations for loosely-associated components in a container.  For
example, each process running on a host might get its configuration
section from that host's section of a shared configuration file.

The top level of a configuration file consists of a series of
inclusions, key-value pairs, and sections.

Comments can be added on lines by themselves.  A comment has a
``#`` as the first non-space character and extends to the end
of the line::

  # This is a comment


An inclusion is expressed like this::

  %include defaults.conf


The resource to be included can be specified by a relative or absolute
URL, resolved relative to the URL of the resource the
``%include`` directive is located in.


A key-value pair is expressed like this::

  key value


The key may include any non-white characters except for parentheses.
The value contains all the characters between the key and the end of
the line, with surrounding whitespace removed.

Since comments must be on lines by themselves, the ``#``
character can be part of a value::

  key value # still part of the value


Sections may be either empty or non-empty.  An empty section may be
used to provide an alias for another section.

A non-empty section starts with a header, contains configuration
data on subsequent lines, and ends with a terminator.

The header for a non-empty section has this form (square brackets
denote optional parts):

.. parsed-literal::

  <*section-type* **[name]**>


*section-type* and *name* all have the same syntactic
constraints as key names.

The terminator looks like this:

.. parsed-literal::

  </*section-type*>


The configuration data in a non-empty section consists of a sequence
of one or more key-value pairs and sections.  For example:

.. code-block:: xml

  <my-section>
    key-1 value-1
    key-2 value-2

    <another-section>
        key-3 value-3
    </another-section>
  </my-section>


(The indentation is used here for clarity, but is not required for
syntactic correctness.)

The header for empty sections is similar to that of non-empty
sections, but there is no terminator:

.. parsed-literal::

  <*section-type* **[name]** />



Extending the Configuration Schema
----------------------------------

As we'll see in :ref:`Writing Configuration Schema <writing-schema>`
what can be written in a configuration is controlled by schemas which
can be built from **components**. These components can also be used
to extend the set of implementations of objects the application can
handle. What this means when writing a configuration is that
third-party implementations of application object types can be used
wherever those application types are used in the configuration, if
there's a :mod:`ZConfig` component available for that implementation.

The configuration file can use an ``%import`` directive to load
a named component::

  %import Products.Ape


The text to the right of the ``%import`` keyword must be the
name of a Python package; the :mod:`ZConfig` component provided by
that package will be loaded and incorporated into the schema being
used to load the configuration file.  After the import, section types
defined in the component may be used in the configuration.

More detail is needed for this to really make sense.

A schema may define section types which are **abstract**; these
cannot be used directly in a configuration, but multiple concrete
section types can be defined which **implement** the abstract
types.  Wherever the application allows an abstract type to be used,
any concrete type which implements that abstract type can be used in
an actual configuration.

The ``%import`` directive allows loading schema components
which provide alternate concrete section types which implement the
abstract types defined by the application.  This allows third-party
implementations of abstract types to be used in place of or in
addition to implementations provided with the application.

Consider an example application which supports logging in
the same way Zope 2 does.  There are some parameters which configure
the general behavior of the logging mechanism, and an arbitrary number
of **log handlers** may be specified to control how the log
messages are handled.  Several log handlers are provided by the
application.  Here is an example logging configuration:

.. code-block:: xml


  <eventlog>
    level verbose

    <logfile>
      path /var/log/myapp/events.log
    </logfile>
  </eventlog>


A third-party component may provide a log handler to send
high-priority alerts the system administrator's text pager or
SMS-capable phone.  All that's needed is to install the implementation
so it can be imported by Python, and modify the configuration::


  %import my.pager.loghandler

  <eventlog>
    level verbose

    <logfile>
      path /var/log/myapp/events.log
    </logfile>

    <pager>
      number   1-800-555-1234
      message  Something broke!
    </pager>
  </eventlog>


Other Examples
--------------

Other examples of configuration files can be found at :ref:`using-logging`.

Textual Substitution in Values
------------------------------

:mod:`ZConfig` provides a limited way to re-use portions of a value
using simple string substitution.  To use this facility, define named
bits of replacement text using the ``%define`` directive, and
reference these texts from values.

The syntax for ``%define`` is:

.. parsed-literal::

  %define *name* [*value*]


The value of *name* must be a sequence of letters, digits, and
underscores, and may not start with a digit; the namespace for these
names is separate from the other namespaces used with
:mod:`ZConfig`, and is case-insensitive.  If *value* is
omitted, it will be the empty string.  If given, there must be
whitespace between *name* and *value*; *value* will not
include any whitespace on either side, just like values from key-value
pairs.

Names must be defined before they are used, and may not be
re-defined with a different value.  All resources being parsed as part of
a configuration share a single namespace for defined names.

References to defined names from configuration values use the syntax
described for the :mod:`ZConfig.substitution` module.
Configuration values which include a ``$`` as part of the
actual value will need to use ``$$`` to get a single
``$`` in the result.

The values of defined names are processed in the same way as
configuration values, and may contain references to named
definitions.

For example, the value for ``key`` will evaluate to ``value``::


  %define name value
  key $name


Substitution in Values from Environment Variables
-------------------------------------------------

Values in :mod:`ZConfig` can be substituted from environment variables.
It utilizes Pythons ``os.getenv`` to fetch the values. Syntax is a ``$``
followed by round brackets (parentheses). In this example the variable
key gets a value assigned from the enviroment named ENVKEY::

  key $(ENVKEY)

Further details and examples are described in the :mod:`ZConfig.substitution`
module.
