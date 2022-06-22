=====================
 Configuring Logging
=====================

One common use of ZConfig is to configure the Python :mod:`logging`
framework. ZConfig provides one simple convenience function to do this:

.. autofunction:: ZConfig.configureLoggers

Suppose we have the following logging configuration in a file called ``simple-root-config.conf``:

.. literalinclude:: simple-root-config.conf
   :language: xml

We can load this file and pass its contents to ``configureLoggers``:

.. code-block:: python

    from ZConfig import configureLoggers
    with open('simple-root-config.conf') as f:
        configureLoggers(f.read())

.. -> src
  >>> import six
  >>> six.exec_(src)

When this returns, the root logger is configured to output messages
logged at INFO or above to the console, as we can see in the following
example:

.. code-block:: pycon

    >>> from logging import getLogger
    >>> getLogger().info('We see an info message')
    INFO root We see an info message
    >>> getLogger().debug('We do not see a debug message')

A more common configuration would see STDOUT replaced with a path to
the file into which log entries would be written.

Although loading configuration from a file is common, we could of
course also pass a string literal to :func:`~.configureLoggers`. Any
type of Python string (bytes or unicode) is acceptable.


Configuration Format
====================

The configuration text is in the :ref:`ZConfig format <syntax>` and
supports comments and substitutions.

It can contain multiple ``<logger>`` elements,
each of which can have any number of :ref:`handler elements <logging-handlers>`.

.. zconfig:: ZConfig.components.logger
    :file: logger.xml
    :members: logger

.. highlight:: xml

Examples
--------

Here's the configuration we looked at above. It configures the root
(unnamed) logger with one handler (``<logfile>``), operating at the INFO level:

.. literalinclude:: simple-root-config.conf
   :language: xml

We can configure a different logger in the hierarchy to use the DEBUG
level at the same time as we configure the root logger. We're not
specifying a handler for it, but the default ``propagate`` value will
let the lower level logger use the root logger's handler:

.. literalinclude:: root-and-child-config.conf
   :language: xml


If we load that configuration from ``root-and-child-config.conf``, we
can expect this behaviour:

..
  >>> resetLoggers()

.. code-block:: pycon

    >>> with open('root-and-child-config.conf') as f:
    ...     configureLoggers(f.read())
    >>> getLogger().info('Here is another info message')
    INFO root Here is another info message
    >>> getLogger().debug('This debug message is hidden')
    >>> getLogger('my.package').debug('The debug message for my.package shows')
    DEBUG my.package The debug message for my.package shows

.. _logging-handlers:

Log Handlers
============

Many of Python's built-in log handlers can be configured with ZConfig.


Files
-----

The ``<logfile>`` handler writes to files or standard output or standard error
(when the ``path`` is ``STDOUT`` or ``STDERR`` respectively). It
configures a :class:`logging.FileHandler` or :class:`logging.StreamHandler`.
When the ``when`` or ``max-size`` attributes are set, the files on disk
will be rotated either at :class:`set intervals
<logging.handlers.TimedRotatingFileHandler>` or when files
:class:`reach the set size <logging.handlers.RotatingFileHandler>`,
respectively.

.. zconfig:: ZConfig.components.logger
     :file: handlers.xml
     :members: logfile

The System Log
--------------

The ``<syslog>`` handler configures the :class:`logging.handlers.SysLogHandler`.

.. zconfig:: ZConfig.components.logger
     :file: handlers.xml
     :members: syslog

Windows Event Log
-----------------

On Windows, the ``<win32-eventlog>`` configures the :class:`logging.handlers.NTEventLogHandler`.

.. zconfig:: ZConfig.components.logger
     :file: handlers.xml
     :members: win32-eventlog

HTTP
----

The ``<<http-logger>`` element configures :class:`logging.handlers.HTTPHandler`.

.. zconfig:: ZConfig.components.logger
     :file: handlers.xml
     :members: http-logger


Email
-----

ZConfig has support for Python's :class:`logging.handlers.SMTPHandler`
via the ``<email-notifier>`` handler.

.. zconfig:: ZConfig.components.logger
     :file: handlers.xml
     :members: email-notifier
