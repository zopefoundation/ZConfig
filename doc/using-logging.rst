=====================
 Configuring Logging
=====================

One common use of ZConfig is to configure the Python :mod:`logging`
framework. ZConfig provides one simple convenience function to do this:

.. autofunction:: ZConfig.configureLoggers


This function takes the configuration text::

    >>> from ZConfig import configureLoggers
    >>> configureLoggers('''
    ... <logger>
    ...    level INFO
    ...    <logfile>
    ...       PATH STDOUT
    ...       format %(levelname)s %(name)s %(message)s
    ...    </logfile>
    ... </logger>
    ... ''')

When this returns, the root logger is configured to output messages
logged at INFO or above to the console, as we can see in the following
example::

    >>> from logging import getLogger
    >>> logger = getLogger()
    >>> logger.info('An info message')
    INFO root An info message
    >>> logger.debug('A debug message')

A more common configuration would see STDOUT replaced with a path to
the file into which log entries would be written.

You can read the logging configuration from a file and pass it to
:func:`~.configureLoggers`. Any type of Python string (bytes or
unicode) is acceptable.


Configuration Format
====================

The configuration text is in the :ref:`ZConfig format <syntax>` and
supports comments and substitutions.

It can contain multiple ``<logger>`` elements,
each of which can have any number of :ref:`handler elements <logging-handlers>`.


.. zconfig:: ZConfig.components.logger
    :file: logger.xml
    :members: logger


.. _logging-handlers:

Log Handlers
============

Many of Python's built-in log handlers can be configured with ZConfig.

.. highlight:: xml

Files
-----

The ``<logfile>`` handler writes to files or standard output or standard error
(when the ``path`` is ``STDOUT`` or ``STDERR`` respectively). It
configures a :class:`logging.StreamHandler`. When the
``interval`` or ``max-size`` attributes are set, the files on disk
will be rotated either at :class:`set intervals
<logging.handlers.TimedRotatingFileHandler>` or when files
:class:`reach the set size <logging.handlers.RotatingFileHandler>`, respectively.

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
