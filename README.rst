ZConfig: Schema-driven configuration
====================================

.. image:: https://img.shields.io/pypi/v/ZConfig.svg
        :target: https://pypi.python.org/pypi/ZConfig/
        :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/ZConfig.svg
        :target: https://pypi.org/project/ZConfig/
        :alt: Supported Python versions

.. image:: https://github.com/zopefoundation/ZConfig/actions/workflows/tests.yml/badge.svg
        :target: https://github.com/zopefoundation/ZConfig/actions/workflows/tests.yml

.. image:: https://coveralls.io/repos/github/zopefoundation/ZConfig/badge.svg?branch=master
        :target: https://coveralls.io/github/zopefoundation/ZConfig?branch=master

.. image:: https://readthedocs.org/projects/zconfig/badge/?version=latest
        :target: http://zconfig.readthedocs.org/en/latest/
        :alt: Documentation Status

ZConfig is a configuration library intended for general use.  It
supports a hierarchical schema-driven configuration model that allows
a schema to specify data conversion routines written in Python.
ZConfig's model is very different from the model supported by the
ConfigParser module found in Python's standard library, and is more
suitable to configuration-intensive applications.

ZConfig schema are written in an XML-based language and are able to
"import" schema components provided by Python packages.  Since
components are able to bind to conversion functions provided by Python
code in the package (or elsewhere), configuration objects can be
arbitrarily complex, with values that have been verified against
arbitrary constraints.  This makes it easy for applications to
separate configuration support from configuration loading even with
configuration data being defined and consumed by a wide range of
separate packages.

ZConfig is licensed under the Zope Public License, version 2.1.  See
the file LICENSE.txt in the distribution for the full license text.

Reference documentation is available at https://zconfig.readthedocs.io.

Information on the latest released version of the ZConfig package is
available at

  https://pypi.org/project/ZConfig/

You may either create an RPM and install this, or install directly from
the source distribution.

There is a mailing list for discussions and questions about ZConfig;
more information on the list is available at

  http://mail.zope.org/mailman/listinfo/zconfig/


Configuring Logging
-------------------

One common use of ZConfig is to configure the Python logging
framework. This is extremely simple to do as the following example
demonstrates:

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

The above configures the root logger to output messages logged at INFO
or above to the console, as we can see in the following example:

    >>> from logging import getLogger
    >>> logger = getLogger()
    >>> logger.info('An info message')
    INFO root An info message
    >>> logger.debug('A debug message')

A more common configuration would see STDOUT replaced with a path to
the file into which log entries would be written.

For more information, see the `the documentation <https://zconfig.readthedocs.io>`_.


Installing from the source distribution
---------------------------------------

For a simple installation::

  python setup.py install


To install to a user's home-dir::

  python setup.py install --home=<dir>


To install to another prefix (for example, /usr/local)::

  python setup.py install --prefix=/usr/local


For more information on installing packages, please refer to the
`Python Packaging User Guide <https://packaging.python.org/>`__.
