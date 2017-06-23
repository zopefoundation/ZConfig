==============================
 Writing Configuration Schema
==============================


Configurations which use :mod:`ZConfig` are described using
:ref:`"schema" <writing-schema>`. A schema is a specification for the
allowed structure and content of the configuration. :mod:`ZConfig`
schema are written using a small XML-based language. The schema
language allows the schema author to specify the names of the keys
allowed at the top level and within sections, to define the types of
sections which may be used (and where), the types of each values,
whether a key or section must be specified or is optional, default
values for keys, and whether a value can be given only once or
repeatedly.

.. _writing-schema:

Writing Configuration Schema
============================

Data types are searched in a special namespace defined by the data
type registry.  The default registry has slightly magical semantics:
If the value can be matched to a standard data type when interpreted
as a **basic-key**, the standard data type will be used.  If
that fails, the value must be a **dotted-name** containing at
least one dot, and a conversion function will be sought using the
:meth:`~.search` method of the data type registry used to load the
schema.

.. _elements:

Schema Elements
---------------

For each element, the content model is shown, followed by a
description of how the element is used, and then a list of the
available attributes.  For each attribute, the type of the value is
given as either the name of a :mod:`ZConfig` datatype or an XML
attribute value type.  Familiarity with XML's Document Type Definition
language is helpful.

The following elements are used to describe a schema:

.. code-block:: xml

 <schema>
   description?, metadefault?, example?, import*, (sectiontype |
   abstracttype)*, (section | key | multisection | multikey)*
 </schema>

Document element for a :mod:`ZConfig` schema.

**extends** (**space-separated-url-references**)
    A list of URLs of base schemas from which this section type will inherit
    key, section, and section type declarations.  If omitted, this schema is
    defined using only the keys, sections, and section types contained within
    the ``schema`` element.

**datatype** (**basic-key** or **dotted-name**)
    The data type converter which will be applied to the value of this
    section.  If the value is a **dotted-name** that begins
    with a period, the value of ``prefix``  will be pre-pended,
    if set.  If any base schemas are listed in the ``extends``
    attribute, the default value for this attribute comes from the base
    schemas.  If the base schemas all use the same ``datatype`` , then
    that data type will be the default value for the extending schema.  If
    there are no base schemas, the default value is **null** , which
    means that the :mod:`ZConfig` section object will be used unconverted.
    If the base schemas have different ``datatype``  definitions, you
    must explicitly define the ``datatype``  in the extending schema.

**handler** (**basic-key**)

**keytype** (**basic-key** or **dotted-name**)
    The data type converter which will be applied to keys found in
    this section.  This can be used to constrain key values in
    different ways; two data types which may be especially useful are
    the **identifier** and **ipaddr-or-hostname**
    types.  If the value is a **dotted-name** that begins
    with a period, the value of ``prefix``  will be pre-pended,
    if set.  If any base schemas are listed in the ``extends``
    attribute, the default value for this attribute comes from the base
    schemas.  If the base schemas all use the same ``keytype`` , then
    that key type will be the default value for the extending schema.  If there
    are no base schemas, the default value is **basic-key** .  If the
    base schemas have different ``keytype``  definitions, you must
    explicitly define the ``keytype``  in the extending schema.


**prefix** (**dotted-name**)
    Prefix to be pre-pended in front of partial dotted-names that
    start with a period.  The value of this attribute is used in all
    contexts with the ``schema``  element if it hasn't been
    overridden by an inner element with a ``prefix``
    attribute.

.. code-block:: xml

  <description>
     PCDATA
  </description>

Descriptive text explaining the purpose the container of the
``description``  element.  Most other elements can contain
a ``description``  element as their first child.
At most one ``description``  element may appear in a given
context.

**format** (NMTOKEN)
   Optional attribute that can be added to indicate what conventions
    are used to mark up the contained text.  This is intended to serve
    as a hint for documentation extraction tools.  Suggested values
    are:

    =========      ===============================================
    Value          Content Format
    =========      ===============================================
    ``plain``      ``text/plain``; blank lines separate paragraphs
    ``rest``       reStructuredText
    ``stx``        Classic Structured Text
    =========      ===============================================

.. code-block:: xml

  <example>
     PCDATA
  </example>

An example value.  This serves only as documentation.

.. code-block:: xml

  <metadefault>
    PCDATA
  </metadefault>

A description of the default value, for human readers.  This may
include information about how a computed value is determined when
the schema does not specify a default value.

.. code-block:: xml

  <abstracttype>
     description?
  </abstracttype>

Define an abstract section type.

**name** (**basic-key**)
    The name of the abstract section type; required.

.. code-block:: xml

  <sectiontype>
     description?, example?, (section | key | multisection | multikey)*
  </sectiontype>

Define a concrete section type.

**datatype** (**basic-key** or **dotted-name**)
    The data type converter which will be applied to the value of this
    section.  If the value is a **dotted-name** that begins
    with a period, the value of ``prefix``  will be pre-pended,
    if set.  If ``datatype``  is omitted and
    ``extends`` is used, the ``datatype`` from the
    section type identified by the ``extends``  attribute is
    used.


**extends** (**basic-key**)
    The name of a concrete section type from which this section type
    acquires all key and section declarations.  This type does
    **not** automatically implement any abstract section type
    implemented by the named section type.  If omitted, this section
    is defined with only the keys and sections contained within the
    ``sectiontype``  element.  The new section type is called a
    **derived** section type, and the type named by this attribute
    is called the **base** type.  Values for the
    ``datatype`` and ``keytype`` attributes are
    acquired from the base type if not specified.


**implements** (**basic-key**)
    The name of an abstract section type which this concrete section
    type implements.  If omitted, this section type does not implement
    any abstract type, and can only be used if it is specified
    directly in a schema or other section type.


**keytype** (**basic-key**)
    The data type converter which will be applied to keys found in
    this section.  This can be used to constrain key values in
    different ways; two data types which may be especially useful are
    the **identifier** and **ipaddr-or-hostname**
    types.  If the value is a **dotted-name** that begins
    with a period, the value of ``prefix``  will be pre-pended,
    if set.  The default value is **basic-key** .  If
    ``keytype`` is omitted and ``extends`` is used,
    the ``keytype``  from the section type identified by the
    ``extends``  attribute is used.


**name** (**basic-key**)
    The name of the section type; required.


**prefix** (**dotted-name**)
    Prefix to be pre-pended in front of partial dotted-names that
    start with a period.  The value of this attribute is used in all
    contexts in the ``sectiontype``  element.  If omitted, the
    prefix specified by a containing context is used if specified.

.. code-block:: xml

  <import>
    EMPTY
  </import>

Import a schema component.  Exactly one of the attributes
``package`` and ``src`` must be specified.

**file** (file name without directory information}
    Name of the component file within a package; if not specified,
    'component.xml' is used.  This may only be given when
    ``package`` is used.  (The 'component.xml' file is
    always used when importing via ``%import`` from a
    configuration file.)


**package** (**dotted-suffix**)
    Name of a Python package that contains the schema component being
    imported.  The component will be loaded from the file identified
    by the ``file`` attribute, or 'component.xml' if
    ``file``  is not specified.  If the package name given
    starts with a dot (``.``), the name used will be the
    current prefix and the value of this attribute concatenated.


**src** (**url-reference**)
    URL to a separate schema which can provide useful types.  The
    referenced resource must contain a schema, not a schema
    component.  Section types defined or imported by the referenced
    schema are added to the schema containing the ``import`` ;
    top-level keys and sections are ignored.

.. code-block:: xml

  <key>
    description?, example?, metadefault?, default*
  </key>

A ``key``  element is used to describe a key-value pair which
may occur at most once in the section type or top-level schema in
which it is listed.

**attribute** (**identifier**)
    The name of the Python attribute which this key should be the
    value of on a :class:`SectionValue` instance.  This must be unique
    within the immediate contents of a section type or schema.  If
    this attribute is not specified, an attribute name will be
    computed by converting hyphens in the key name to underscores.


**datatype** (**basic-key** or **dotted-name**)
    The data type converter which will be applied to the value of this
    key.  If the value is a **dotted-name** that begins
    with a period, the value of ``prefix``  will be pre-pended,
    if set.


**default** (**string**)
    If the key-value pair is optional and this attribute is specified,
    the value of this attribute will be converted using the appropriate
    data type converter and returned to the application as the
    configured value.  This attribute may not be specified if the
    ``required`` attribute is ``yes``.


**handler** (**basic-key**)


**name** (**basic-key**)
    The name of the key, as it must be given in a configuration
    instance, or ``*``.  If the value is ``*``, any name not
    already specified as a key may be used, and the configuration
    value for the key will be a dictionary mapping from the key name
    to the value.  In this case, the ``attribute``  attribute
    must be specified, and the data type for the key will be applied
    to each key which is found.


**required** (``yes|no``)
    Specifies whether the configuration instance is required to
    provide the key.  If the value is ``yes``, the
    ``default``  attribute may not be specified and an error
    will be reported if the configuration instance does not specify a
    value for the key.  If the value is ``no`` (the default) and
    the configuration instance does not specify a value, the value
    reported to the application will be that specified by the
    ``default`` attribute, if given, or ``None``.

.. code-block:: xml

  <multikey>
    description?, example?, metadefault?, default*
  </multikey>

A ``multikey``  element is used to describe a key-value pair
which may occur any number of times in the section type or top-level
schema in which it is listed.

**attribute** (**identifier**)
    The name of the Python attribute which this key should be the
    value of on a :class`SectionValue` instance.  This must be unique
    within the immediate contents of a section type or schema.  If
    this attribute is not specified, an attribute name will be
    computed by converting hyphens in the key name to underscores.


**datatype** (**basic-key** or **dotted-name**)
    The data type converter which will be applied to the value of this
    key.  If the value is a **dotted-name** that begins
    with a period, the value of ``prefix``  will be pre-pended,
    if set.


**handler** (**basic-key**)


**name** (**basic-key**)
    The name of the key, as it must be given in a configuration
    instance, or ``+``.  If the value is ``+``, any name not
    already specified as a key may be used, and the configuration
    value for the key will be a dictionary mapping from the key name
    to the value.  In this case, the ``attribute``  attribute
    must be specified, and the data type for the key will be applied
    to each key which is found.


**required** (``yes|no``)
    Specifies whether the configuration instance is required to
    provide the key.  If the value is ``yes``, no ``default``
    elements may be specified and an error will be reported if the
    configuration instance does not specify at least one value for the
    key.  If the value is ``no`` (the default) and the
    configuration instance does not specify a value, the value
    reported to the application will be a list containing one element
    for each ``default``  element specified as a child of the
    ``multikey`` .  Each value will be individually converted
    according to the ``datatype``  attribute.

.. code-block:: xml

  <default>
    PCDATA
  </default>

Each ``default``  element specifies a single default value for
a ``multikey`` .  This element can be repeated to produce a
list of individual default values.  The text contained in the
element will be passed to the datatype conversion for the
``multikey`` .

**key** (key type of the containing sectiontype}
    Key to associate with the default value.  This is only used for
    defaults of a ``key`` or ``multikey`` with a
    ``name`` of ``+``; in that case this attribute is
    required.  It is an error to use the ``key``  attribute
    with a ``default`` element for a ``multikey`` with a
    name other than ``+``.

.. warning::
      The datatype of this attribute is that of the section type
      **containing** the actual keys, not necessarily that of the
      section type which defines the key.  If a derived section
      overrides the key type of the base section type, the actual
      key type used is that of the derived section.

      This can lead to confusing errors in schemas, though the
      :mod:`ZConfig` package checks for this when the schema is
      loaded.  This situation is particularly likely when a derived
      section type uses a key type which collapses multiple default
      keys which were not collapsed by the base section type.

      Consider this example schema:

      .. code-block:: xml


        <schema>
          <sectiontype name="base" keytype="identifier">
             <key name="+" attribute="mapping">
               <default key="foo">some value</default>
               <default key="FOO">some value</default>
             </key>
           </sectiontype>

           <sectiontype name="derived" keytype="basic-key"
                 extends="base"/>

           <section type="derived" name="*" attribute="section"/>
         </schema>


      When this schema is loaded, a set of defaults for the
      **derived** section type is computed.  Since
      **basic-key** is case-insensitive (everything is
      converted to lower case), ``foo`` and ``Foo`` are both
      converted to ``foo``, which clashes since ``key``  only
      allows one value for each key.

.. code-block:: xml

  <section>
    description?, example?
  </section>

A ``section``  element is used to describe a section which may
occur at most once in the section type or top-level schema in which
it is listed.

**attribute** (**identifier**)
    The name of the Python attribute which this section should be the
    value of on a :class:`SectionValue` instance.  This must be unique
    within the immediate contents of a section type or schema.  If
    this attribute is not specified, an attribute name will be
    computed by converting hyphens in the section name to underscores,
    in which case the ``name`` attribute may not be ``*``
    or ``+``.


**handler** (**basic-key**)


**name** (**basic-key**)
    The name of the section, as it must be given in a configuration
    instance, ``*``, or ``+``.  If the value is ``*`` or this
    attribute is omitted, any name not already specified as a key may
    be used.  If the value is ``*`` or ``+``, the
    ``attribute``  attribute must be specified.  If the value
    is ``*``, any name is allowed, or the name may be omitted.  If
    the value is ``+``, any name is allowed, but some name must be
    provided.


**required** (``yes|no``)
    Specifies whether the configuration instance is required to
    provide the section.  If the value is ``yes``, an error will be
    reported if the configuration instance does not include the
    section.  If the value is ``no`` (the default) and the
    configuration instance does not include the section, the value
    reported to the application will be ``None``.


**type** (**basic-key**)
    The section type which matching sections must implement.  If the
    value names an abstract section type, matching sections in the
    configuration file must be of a type which specifies that it
    implements the named abstract type.  If the name identifies a
    concrete type, the section type must match exactly.

.. code-block:: xml

  <multisection>
    description?, example?
  </multisection>

A ``multisection``  element is used to describe a section which
may occur any number of times in the section type or top-level
schema in which it is listed.

**attribute** (**identifier**)
    The name of the Python attribute which matching sections should be
    the value of on a :class:`SectionValue` instance.  This is required
    and must be unique within the immediate contents of a section type
    or schema.  The :class:`SectionValue` instance will contain a list
    of matching sections.


**handler** (**basic-key**)


**name** (**basic-key**)
    For a ``multisection`` , any name not already specified as a
    key may be used.  If the value is ``*`` or ``+``, the
    ``attribute``  attribute must be specified.  If the value
    is ``*`` or this attribute is omitted, any name is allowed, or
    the name may be omitted.  If the value is ``+``, any name is
    allowed, but some name must be provided.  No other value for the
    ``name``  attribute is allowed for a
    ``multisection`` .


**required** (``yes|no``)
    Specifies whether the configuration instance is required to
    provide at least one matching section.  If the value is
    ``yes``, an error will be reported if the configuration
    instance does not include the section.  If the value is ``no``
    (the default) and the configuration instance does not include the
    section, the value reported to the application will be
    ``None``.


**type** (**basic-key**)
    The section type which matching sections must implement.  If the
    value names an abstract section type, matching sections in the
    configuration file must be of types which specify that they
    implement the named abstract type.  If the name identifies a
    concrete type, the section type must match exactly.


.. _schema-components:

Schema Components
-----------------

.. XXX need more explanation

:mod:`ZConfig` supports schema components that can be
provided by disparate components, and allows them to be knit together
into concrete schema for applications.  Components cannot add
additional keys or sections in the application schema.

A schema *component* is allowed to define new abstract and section
types. Components are identified using a dotted-name, similar to a
Python module name. For example, one component may be
``zodb.storage``.

Schema components are stored alongside application code since they
directly reference datatype code.  Schema components are provided by
Python packages.  The component definition is normally stored in the
file 'component.xml'; an alternate filename may be specified
using the ``file``  attribute of the ``import``  element.
Components imported using the ``%import`` keyword from a
configuration file must be named 'component.xml'.
The component defines the types provided by that component; it must
have a ``component``  element as the document element.

The following element is used as the document element for schema
components.  Note that schema components do not allow keys and
sections to be added to the top-level of a schema; they serve only to
provide type definitions.

.. code-block:: xml

  <component>
    description?, (abstracttype | sectiontype)*
  </component>

The top-level element for schema components.

**prefix** (**dotted-name**)
    Prefix to be pre-pended in front of partial dotted-names that
    start with a period.  The value of this attribute is used in all
    contexts within the ``component``  element if it hasn't been
    overridden by an inner element with a ``prefix``
    attribute.


Referring to Files in Packages
------------------------------

The ``extends``  attribute of the ``schema``  element is
used to refer to files containing base schema; sometimes it makes
sense to refer to a base schema relative to the Python package that
provides it.  For this purpose, ZConfig supports the special
``package:`` URL scheme.

The ``package:`` URL scheme is straightforward, and contains three
parts: the scheme name, the package name, and a relative path.  The
relative path is searched for using the named package's
``__path__`` if it's a conventional filesystem package, or using
the package's loader if that supports resource access (such as the
loader for eggs and other ZIP-file based packages).

The basic form of the ``package:`` URL is:

.. parsed-literal::

  package:*package.name*:*relative-path*


The package name must be fully specified; the current prefix, if any,
is not used.  If the named package is contained in an egg or ZIP file,
the resource identified by the relative path must reside in the same
egg or ZIP file.

The ``package:`` URL scheme is generally available everywhere
ZConfig supports loading text from URLs directly, but applications
using ZConfig do not automatically acquire general support for this.


.. _schema-dtd:

Schema Document Type Definition
===============================

The following is the XML Document Type Definition for :mod:`ZConfig`
schema:

.. literalinclude:: schema.dtd
   :language: dtd
