.. _standard-components:

===========================================
 Standard :mod:`ZConfig` Schema Components
===========================================

:mod:`ZConfig` provides a few convenient schema components as part
of the package.  These may be used directly or can server as examples
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


ZConfig.components.logger
=========================

The :mod:`ZConfig.components.logger` package provides configuration
support for the :mod:`logging` package in Python's standard library.
This component can be imported using::


  <import package="ZConfig.components.logger"/>


This component defines two abstract types and several concrete section
types.  These can be imported as a unit, as above, or as four smaller
components usable in creating alternate logging packages.

The first of the four smaller components contains the abstract types,
and can be imported using::


  <import package="ZConfig.components.logger" file="abstract.xml"/>


The two abstract types imported by this are:


**ZConfig.logger.log**
  Logger objects are represented by this abstract type.

**ZConfig.logger.handler**
  Each logger object can have one or more "handlers" associated with
  them.  These handlers are responsible for writing logging events to
  some form of output stream using appropriate formatting.  The output
  stream may be a file on a disk, a socket communicating with a server
  on another system, or a series of ``syslog`` messages.  Section
  types which implement this type represent these handlers.


The second and third of the smaller components provides section types
that act as factories for :class:`logging.Logger` objects.  These can be
imported using::


  <import package="ZConfig.components.logger" file="eventlog.xml"/>
  <import package="ZConfig.components.logger" file="logger.xml"/>

The types defined in these components implement the
**ZConfig.logger.log** abstract type.  The 'eventlog.xml'
component defines an **eventlog** type which represents the
root logger from the the :mod:`logging` package (the return value of
:func:`logging.getLogger`), while the 'logger.xml' component
defines a **logger** section type which represents a named
logger.


The third of the smaller components provides section types that are
factories for :class:`logging.Handler` objects.  This can be imported
using::


  <import package="ZConfig.components.logger" file="handlers.xml"/>


The types defined in this component implement the
**ZConfig.logger.handler** abstract type.


The configuration objects provided by both the logger and handler
types are factories for the finished loggers and handlers.  These
factories should be called with no arguments to retrieve the logger or
log handler objects.  Calling the factories repeatedly will cause the
same objects to be returned each time, so it's safe to simply call
them to retrieve the objects.

The factories for the logger objects, whether the **eventlog**
or **logger** section type is used, provide a :meth:`~.reopen`
method which may be called to close any log files and re-open them.
This is useful when using a UNIX signal to effect log file
rotation: the signal handler can call this method, and not have to
worry about what handlers have been registered for the logger.  There
is also a function in the
:mod:`ZConfig.components.logger.loghandler` module that re-opens all
open log files created using ZConfig configuration:

.. py:function:: ZConfig.components.logger.loghandler.reopenFiles()

  Closes and re-opens all the log files held open by handlers created
  by the factories for ``logfile`` sections.  This is intended to
  help support log rotation for applications.

.. _using-logging:

Using The Logging Components
----------------------------

Building an application that uses the logging components is fairly
straightforward.  The schema needs to import the relevant components
and declare their use::


  <schema>
    <import package="ZConfig.components.logger" file="eventlog.xml"/>
    <import package="ZConfig.components.logger" file="handlers.xml"/>

    <section type="eventlog" name="*" attribute="eventlog"
             required="yes"/>
  </schema>


In the application, the schema and configuration file should be loaded
normally.  Once the configuration object is available, the logger
factory should be called to configure Python's :mod:`logging` package:

.. code-block:: python


  import os
  import ZConfig

  def run(configfile):
    schemafile = os.path.join(os.path.dirname(__file__), "schema.xml")
    schema = ZConfig.loadSchema(schemafile)
    config, handlers = ZConfig.loadConfig(schema, configfile)

    # configure the logging package:
    config.eventlog()

    # now do interesting things


An example configuration file for this application may look like this::


  <eventlog>
    level  info

    <logfile>
      path        /var/log/myapp
      format      %(asctime)s %(levelname)s %(name)s %(message)s
      # locale-specific date/time representation
      dateformat  %c
    </logfile>

    <syslog>
      level    error
      address  syslog.example.net:514
      format   %(levelname)s %(name)s %(message)s
    </syslog>
  </eventlog>


Refer to the :class:`logging.LogRecord` documentation for the names
available in the message format strings (the ``format`` key in the
log handlers).  The date format strings (the ``dateformat`` key in
the log handlers) are the same as those accepted by the
:func:`time.strftime` function.

Configuring the email logger
----------------------------

ZConfig has support for Python's :class:`logging.handlers.SMTPHandler`
via the ``<email-notifier>`` handler::


  <eventlog>
    <email-notifier>
      to sysadmin@example.com
      to john@example.com
      from zlog-user@example.com
      level fatal
      smtp-username john
      smtp-password johnpw
    </email-notifier>
  </eventlog>


For details about the :class:`~logging.handlers.SMTPHandler` see the
Python :mod:`logging` module.
