.. _standard-components:

===========================================
 Standard :mod:`ZConfig` Schema Components
===========================================

:mod:`ZConfig` provides a few convenient schema components as part
of the package.  These may be used directly or can serve as examples
for creating new components.

.. highlight:: xml

ZConfig.components.basic
========================

The :mod:`ZConfig.components.basic` package provides small
components that can be helpful in composing application-specific
components and schema.  There is no large functionality represented by
this package.  The default component provided by this package simply
imports all of the smaller components.  This can be imported using::


  <import package="ZConfig.components.basic"/>


Each of the smaller components is documented directly; importing these
selectively can reduce the time it takes to load a schema slightly,
and allows replacing the other basic components with alternate
components (by using different imports that define the same type
names) if desired.

.. _basic-mapping:

The Mapping Section Type
------------------------

There is a basic section type that behaves like a simple Python
mapping; this can be imported directly using::

  <import package="ZConfig.components.basic" file="mapping.xml"/>


This defines a single section type, **ZConfig.basic.mapping**.
When this is used, the section value is a Python dictionary mapping
keys to string values.

This type is intended to be used by extending it in simple ways.  The
simplest is to create a new section type name that makes more sense
for the application::


  <import package="ZConfig.components.basic" file="mapping.xml"/>

  <sectiontype name="my-mapping"
               extends="ZConfig.basic.mapping"
               />

  <section name="*"
           type="my-mapping"
           attribute="map"
           />

This allows a configuration to contain a mapping from
**basic-key** names to string values like this:

.. code-block:: nginx

  <my-mapping>
    This that
    and the other
  </my-mapping>

The value of the configuration object's ``map`` attribute would
then be the dictionary:

.. code-block:: python

  {'this': 'that',
   'and': 'the other',
   }


(Recall that the **basic-key** data type converts everything to
lower case.)

Perhaps a more interesting application of
**ZConfig.basic.mapping** is using the derived type to override
the ``keytype`` .  If we have the conversion function:

.. code-block:: python

  def email_address(value):
      userid, hostname = value.split("@", 1)
      hostname = hostname.lower()  # normalize what we know we can
      return "%s@%s" % (userid, hostname)

then we can use this as the key type for a derived mapping type::


  <import package="ZConfig.components.basic" file="mapping.xml"/>

  <sectiontype name="email-users"
               extends="ZConfig.basic.mapping"
               keytype="mypkg.datatypes.email_address"
               />

  <section name="*"
           type="email-users"
           attribute="email_users"
           />
