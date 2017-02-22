==========================
Change History for ZConfig
==========================

3.2.0 (unreleased)
------------------

- Drop support for Python 2.6 and 3.2 and add support for Python 3.6.

- Run tests with pypy and pypy3 as well.

- Host docs at https://zconfig.readthedocs.io

- BaseLoader is now an abstract class that cannot be instantiated.

- Allow ``nan``, ``inf`` and ``-inf`` values for floats in
  configurations. See
  https://github.com/zopefoundation/ZConfig/issues/16.

- Scripts ``zconfig`` (for schema validation) and
  ``zconfig_schema2html`` are ported to Python 3.

3.1.0 (2015-10-17)
------------------

- Add ability to do variable substitution from environment variables using
  $() syntax.

3.0.4 (2014-03-20)
------------------

- Added Python 3.4 support.


3.0.3 (2013-03-02)
------------------

- Added Python 3.2 support.


3.0.2 (2013-02-14)
------------------

- Fixed ResourceWarning in BaseLoader.openResource().


3.0.1 (2013-02-13)
------------------

- Removed an accidentally left `pdb` statement from the code.

- Fix a bug in Python 3 with the custom string `repr()` function.


3.0.0 (2013-02-13)
------------------

- Added Python 3.3 support.

- Dropped Python 2.4 and 2.5 support.


2.9.3 (2012-06-25)
------------------

- Fixed: port values of 0 weren't allowed.  Port 0 is used to request
  an ephemeral port.


2.9.2 (2012-02-11)
------------------

- Adjust test classes to avoid base classes being considered separate
  test cases by (at least) the "nose" test runner.


2.9.1 (2012-02-11)
------------------

- Make FileHandler.reopen thread safe.


2.9.0 (2011-03-22)
------------------

- Allow identical redefinition of ``%define`` names.
- Added support for IPv6 addresses.


2.8.0 (2010-04-13)
------------------

- Fix relative path recognition.
  https://bugs.launchpad.net/zconfig/+bug/405687

- Added SMTP authentication support for email logger on Python 2.6.


2.7.1 (2009-06-13)
------------------

- Improved documentation

- Fixed tests failures on windows.


2.7.0 (2009-06-11)
------------------

- Added a convenience function, ``ZConfig.configureLoggers(text)`` for
  configuring loggers.

- Relaxed the requirement for a logger name in logger sections,
  allowing the logger section to be used for both root and non-root
  loggers.


2.6.1 (2008-12-05)
------------------

- Fixed support for schema descriptions that override descriptions from a base
  schema.  If multiple base schema provide descriptions but the derived schema
  does not, the first base mentioned that provides a description wins.
  https://bugs.launchpad.net/zconfig/+bug/259475

- Fixed compatibility bug with Python 2.5.0.

- No longer trigger deprecation warnings under Python 2.6.


2.6.0 (2008-09-03)
------------------

- Added support for file rotation by time by specifying when and
  interval, rather than max-size, for log files.

- Removed dependency on setuptools from the setup.py.


2.5.1 (2007-12-24)
------------------

- Made it possible to run unit tests via 'python setup.py test' (requires
  setuptools on sys.path).

- Added better error messages to test failure assertions.


2.5 (2007-08-31)
------------------------

*A note on the version number:*

Information discovered in the revision control system suggests that some
past revision has been called "2.4", though it is not clear that any
actual release was made with that version number.  We're going to skip
revision 2.4 entirely to avoid potential issues with anyone using
something claiming to be ZConfig 2.4, and go straight to version 2.5.

- Add support for importing schema components from ZIP archives (including
  eggs).

- Added a 'formatter' configuration option in the logging handler sections
  to allow specifying a constructor for the formatter.

- Documented the package: URL scheme that can be used in extending schema.

- Added support for reopening all log files opened via configurations using
  the ZConfig.components.logger package.  For Zope, this is usable via the
  ``zc.signalhandler`` package.  ``zc.signalhandler`` is not required for
  ZConfig.

- Added support for rotating log files internally by size.

- Added a minimal implementation of schema-less parsing; this is mostly
  intended for applications that want to read several fragments of ZConfig
  configuration files and assemble a combined configuration.  Used in some
  ``zc.buildout`` recipes.

- Converted to using ``zc.buildout`` and the standard test runner from
  ``zope.testing``.

- Added more tests.


2.3.1 (2005-08-21)
------------------

- Isolated some of the case-normalization code so it will at least be
  easier to override.  This remains non-trivial.


2.3 (2005-05-18)
----------------

- Added "inet-binding-address" and "inet-connection-address" to the
  set of standard datatypes.  These are similar to the "inet-address"
  type, but the default hostname is more sensible.  The datatype used
  should reflect how the value will be used.

- Alternate rotating logfile handler for Windows, to avoid platform
  limitations on renaming open files.  Contributed by Sidnei da Silva.

- For <section> and <multisection>, if the name attribute is omitted,
  assume name="*", since this is what is used most often.


2.2 (2004-04-21)
----------------

- More documentation has been written.

- Added a timedelta datatype function; the input is the same as for
  the time-interval datatype, but the resulting value is a
  datetime.timedelta object.

- Make sure keys specified as attributes of the <default> element are
  converted by the appropriate key type, and are re-checked for
  derived sections.

- Refactored the ZConfig.components.logger schema components so that a
  schema can import just one of the "eventlog" or "logger" sections if
  desired.  This can be helpful to avoid naming conflicts.

- Added a reopen() method to the logger factories.

- Always use an absolute pathname when opening a FileHandler.

- A fix to the logger 'format' key to allow the %(process)d expansion variable
  that the logging package supports.

- A new timedelta built-in datatype was added.  Similar to time-interval
  except that it returns a datetime.timedelta object instead.


2.1 (2004-04-12)
----------------

- Removed compatibility with Python 2.1 and 2.2.

- Schema components must really be in Python packages; the directory
  search has been modified to perform an import to locate the package
  rather than incorrectly implementing the search algorithm.

- The default objects use for section values now provide a method
  getSectionAttributes(); this returns a list of all the attributes of
  the section object which store configuration-defined data (including
  information derived from the schema).

- Default information can now be included in a schema for <key
  name="+"> and <multikey name="+"> by using <default key="...">.

- More documentation has been added to discuss schema extension.

- Support for a Unicode-free Python has been fixed.

- Derived section types now inherit the datatype of the base type if
  no datatype is identified explicitly.

- Derived section types can now override the keytype instead of always
  inheriting from their base type.

- <import package='...'/> makes use of the current prefix if the
  package name begins witha dot.

- Added two standard datatypes:  dotted-name and dotted-suffix.

- Added two standard schema components: ZConfig.components.basic and
  ZConfig.components.logger.


2.0 (2003-10-27)
----------------

- Configurations can import additional schema components using a new
  "%import" directive; this can be used to integrate 3rd-party
  components into an application.

- Schemas may be extended using a new "extends" attribute on the
  <schema> element.

- Better error messages when elements in a schema definition are
  improperly nested.

- The "zconfig" script can now simply verify that a schema definition
  is valid, if that's all that's needed.


1.0 (2003-03-25)
----------------

- Initial release.
