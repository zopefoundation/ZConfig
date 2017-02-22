##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""Tests for logging configuration via ZConfig."""

import doctest
import logging
import os
import sys
import tempfile
import unittest

import ZConfig

from ZConfig.components.logger import datatypes
from ZConfig.components.logger import handlers
from ZConfig.components.logger import loghandler

from ZConfig._compat import NStringIO as StringIO
from ZConfig._compat import maxsize

class CustomFormatter(logging.Formatter):
    def formatException(self, ei):
        """Format and return the exception information as a string.

        This adds helpful advice to the end of the traceback.
        """
        import traceback
        sio = StringIO()
        traceback.print_exception(ei[0], ei[1], ei[2], file=sio)
        return sio.getvalue() + "... Don't panic!"


def read_file(filename):
    with open(filename) as f:
        return f.read()


class LoggingTestHelper:

    # Not derived from unittest.TestCase; some test runners seem to
    # think that means this class contains tests.

    # XXX This tries to save and restore the state of logging around
    # the test.  Somewhat surgical; there may be a better way.

    def setUp(self):
        self._created = []
        self._old_logger = logging.getLogger()
        self._old_level = self._old_logger.level
        self._old_handlers = self._old_logger.handlers[:]
        self._old_logger.handlers[:] = []
        self._old_logger.setLevel(logging.WARN)

        self._old_logger_dict = logging.root.manager.loggerDict.copy()
        logging.root.manager.loggerDict.clear()

    def tearDown(self):
        logging.root.manager.loggerDict.clear()
        logging.root.manager.loggerDict.update(self._old_logger_dict)

        for h in self._old_logger.handlers:
            self._old_logger.removeHandler(h)
        for h in self._old_handlers:
            self._old_logger.addHandler(h) # pragma: no cover
        self._old_logger.setLevel(self._old_level)

        while self._created:
            os.unlink(self._created.pop())

        self.assertEqual(loghandler._reopenable_handlers, [])
        loghandler.closeFiles()
        loghandler._reopenable_handlers == []

    def mktemp(self):
        fd, fn = tempfile.mkstemp()
        os.close(fd)
        self._created.append(fn)
        return fn

    def move(self, fn):
        nfn = self.mktemp()
        os.rename(fn, nfn)
        return nfn

    _schema = None

    def get_schema(self):
        if self._schema is None:
            sio = StringIO(self._schematext)
            self.__class__._schema = ZConfig.loadSchemaFile(sio)
        return self._schema

    def get_config(self, text):
        conf, handler = ZConfig.loadConfigFile(self.get_schema(),
                                               StringIO(text))
        self.assertTrue(not handler)
        return conf


class TestConfig(LoggingTestHelper, unittest.TestCase):

    _schematext = """
      <schema>
        <import package='ZConfig.components.logger'/>
        <section type='eventlog' name='*' attribute='eventlog'/>
      </schema>
    """

    def test_config_without_logger(self):
        conf = self.get_config("")
        self.assertTrue(conf.eventlog is None)

    def test_config_without_handlers(self):
        logger = self.check_simple_logger("<eventlog/>")
        # Make sure there's a NullHandler, since a warning gets
        # printed if there are no handlers:
        self.assertEqual(len(logger.handlers), 1)
        self.assertTrue(isinstance(logger.handlers[0], loghandler.NullHandler))

        # And it does nothing
        logger.handlers[0].emit(None)
        logger.handlers[0].handle(None)

    def test_factory_without_stream(self):
        factory = self.check_simple_logger_factory("<eventlog>\n"
                                                   "  <logfile>\n"
                                                   "    path STDERR\n"
                                                   "  </logfile>\n"
                                                   "  <logfile>\n"
                                                   "    path STDERR\n"
                                                   "    level info\n"
                                                   "  </logfile>\n"
                                                   "  <logfile>\n"
                                                   "    path STDERR\n"
                                                   "    level debug\n"
                                                   "  </logfile>\n"
                                                   "</eventlog>")

        factory.startup()
        logger = factory.instance

        factory.level = logging.NOTSET
        self.assertEqual(factory.getLowestHandlerLevel(), logging.DEBUG)
        logger.handlers[0].reopen = lambda: None
        factory.reopen()

    def test_with_logfile(self):
        fn = self.mktemp()
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <logfile>\n"
                                          "    path %s\n"
                                          "    level debug\n"
                                          "  </logfile>\n"
                                          "</eventlog>" % fn)
        logfile = logger.handlers[0]
        self.assertEqual(logfile.level, logging.DEBUG)
        self.assertTrue(isinstance(logfile, loghandler.FileHandler))
        logger.removeHandler(logfile)
        logfile.close()

    def test_with_stderr(self):
        self.check_standard_stream("stderr")

    def test_with_stdout(self):
        self.check_standard_stream("stdout")

    def test_with_rotating_logfile(self):
        fn = self.mktemp()
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <logfile>\n"
                                          "    path %s\n"
                                          "    level debug\n"
                                          "    max-size 5mb\n"
                                          "    old-files 10\n"
                                          "  </logfile>\n"
                                          "</eventlog>" % fn)
        logfile = logger.handlers[0]
        self.assertEqual(logfile.level, logging.DEBUG)
        self.assertEqual(logfile.backupCount, 10)
        self.assertEqual(logfile.maxBytes, 5*1024*1024)
        self.assertTrue(isinstance(logfile, loghandler.RotatingFileHandler))
        logger.removeHandler(logfile)
        logfile.close()

    def test_with_timed_rotating_logfile(self):
        fn = self.mktemp()
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <logfile>\n"
                                          "    path %s\n"
                                          "    level debug\n"
                                          "    when D\n"
                                          "    interval 3\n"
                                          "    old-files 11\n"
                                          "  </logfile>\n"
                                          "</eventlog>" % fn)
        logfile = logger.handlers[0]
        self.assertEqual(logfile.level, logging.DEBUG)
        self.assertEqual(logfile.backupCount, 11)
        self.assertEqual(logfile.interval, 86400*3)
        self.assertTrue(isinstance(logfile, loghandler.TimedRotatingFileHandler))
        logger.removeHandler(logfile)
        logfile.close()

    def test_with_timed_rotating_logfile_and_size_should_fail(self):
        fn = self.mktemp()
        self.assertRaises(
            ValueError,
            self.check_simple_logger,
            "<eventlog>\n"
            "  <logfile>\n"
            "    path %s\n"
            "    level debug\n"
            "    max-size 5mb\n"
            "    when D\n"
            "    old-files 10\n"
            "  </logfile>\n"
            "</eventlog>" % fn)

        # Mising old-files
        self.assertRaisesRegexp(
            ValueError,
            "old-files must be set",
            self.check_simple_logger,
            "<eventlog>\n"
            "  <logfile>\n"
            "    path %s\n"
            "    level debug\n"
            "    max-size 5mb\n"
            "    when D\n"
            "  </logfile>\n"
            "</eventlog>" % fn)

        self.assertRaisesRegexp(
            ValueError,
            "max-bytes or when must be set",
            self.check_simple_logger,
            "<eventlog>\n"
            "  <logfile>\n"
            "    path %s\n"
            "    level debug\n"
            "    interval 1\n"
            "    old-files 10\n"
            "  </logfile>\n"
            "</eventlog>" % fn)


    def test_with_rotating_logfile_and_STD_should_fail(self):
        for path in ('STDERR', 'STDOUT'):
            for param in ('old-files 10', 'max-size 5mb'):
                self.assertRaises(
                    ValueError,
                    self.check_simple_logger,
                    "<eventlog>\n"
                    "  <logfile>\n"
                    "    path %s\n"
                    "    level debug\n"
                    "    when D\n"
                    "    %s\n"
                    "  </logfile>\n"
                    "</eventlog>" % (path, param))


    def check_standard_stream(self, name):
        old_stream = getattr(sys, name)
        conf = self.get_config("""
            <eventlog>
              <logfile>
                level info
                path %s
              </logfile>
            </eventlog>
            """ % name.upper())
        self.assertTrue(conf.eventlog is not None)
        # The factory has already been created; make sure it picks up
        # the stderr we set here when we create the logger and
        # handlers:
        sio = StringIO()
        setattr(sys, name, sio)
        try:
            logger = conf.eventlog()
        finally:
            setattr(sys, name, old_stream)
        logger.warning("woohoo!")
        self.assertTrue(sio.getvalue().find("woohoo!") >= 0)

    def test_custom_formatter(self):
        old_stream = sys.stdout
        conf = self.get_config("""
        <eventlog>
        <logfile>
        formatter ZConfig.components.logger.tests.test_logger.CustomFormatter
        level info
        path STDOUT
        </logfile>
        </eventlog>
        """)
        sio = StringIO()
        sys.stdout = sio
        try:
            logger = conf.eventlog()
        finally:
            sys.stdout = old_stream
        try:
            raise KeyError
        except KeyError:
            logger.exception("testing a KeyError")
        self.assertTrue(sio.getvalue().find("KeyError") >= 0)
        self.assertTrue(sio.getvalue().find("Don't panic") >= 0)

    def test_with_syslog(self):
        import socket
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <syslog>\n"
                                          "    level error\n"
                                          "    facility local3\n"
                                          "  </syslog>\n"
                                          "</eventlog>")
        syslog = logger.handlers[0]
        self.assertEqual(syslog.level, logging.ERROR)
        self.assertTrue(isinstance(syslog, loghandler.SysLogHandler))
        syslog.close() # avoid ResourceWarning
        try:
            syslog.socket.close() # ResourceWarning under 3.2
        except socket.SocketError: # pragma: no cover
            pass

    def test_with_http_logger_localhost(self):
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <http-logger>\n"
                                          "    level error\n"
                                          "    method post\n"
                                          "  </http-logger>\n"
                                          "</eventlog>")
        handler = logger.handlers[0]
        self.assertEqual(handler.host, "localhost")
        # XXX The "url" attribute of the handler is misnamed; it
        # really means just the selector portion of the URL.
        self.assertEqual(handler.url, "/")
        self.assertEqual(handler.level, logging.ERROR)
        self.assertEqual(handler.method, "POST")
        self.assertTrue(isinstance(handler, loghandler.HTTPHandler))

    def test_with_http_logger_remote_host(self):
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <http-logger>\n"
                                          "    method get\n"
                                          "    url http://example.com/log/\n"
                                          "  </http-logger>\n"
                                          "</eventlog>")
        handler = logger.handlers[0]
        self.assertEqual(handler.host, "example.com")
        # XXX The "url" attribute of the handler is misnamed; it
        # really means just the selector portion of the URL.
        self.assertEqual(handler.url, "/log/")
        self.assertEqual(handler.level, logging.NOTSET)
        self.assertEqual(handler.method, "GET")
        self.assertTrue(isinstance(handler, loghandler.HTTPHandler))

    def test_with_email_notifier(self):
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <email-notifier>\n"
                                          "    to sysadmin@example.com\n"
                                          "    to sa-pager@example.com\n"
                                          "    from zlog-user@example.com\n"
                                          "    level fatal\n"
                                          "  </email-notifier>\n"
                                          "</eventlog>")
        handler = logger.handlers[0]
        self.assertEqual(handler.toaddrs, ["sysadmin@example.com",
                                           "sa-pager@example.com"])
        self.assertEqual(handler.fromaddr, "zlog-user@example.com")
        self.assertEqual(handler.level, logging.FATAL)

    def test_with_email_notifier_with_credentials(self):
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <email-notifier>\n"
                                          "    to sysadmin@example.com\n"
                                          "    from zlog-user@example.com\n"
                                          "    level fatal\n"
                                          "    smtp-server foo:487\n"
                                          "    smtp-username john\n"
                                          "    smtp-password johnpw\n"
                                          "  </email-notifier>\n"
                                          "</eventlog>")

        self.assertTrue(sys.version_info >= (2, 6))
        handler = logger.handlers[0]
        self.assertEqual(handler.toaddrs, ["sysadmin@example.com"])
        self.assertEqual(handler.fromaddr, "zlog-user@example.com")
        self.assertEqual(handler.fromaddr, "zlog-user@example.com")
        self.assertEqual(handler.level, logging.FATAL)
        self.assertEqual(handler.username, 'john')
        self.assertEqual(handler.password, 'johnpw')
        self.assertEqual(handler.mailhost, 'foo')
        self.assertEqual(handler.mailport, 487)

    def test_with_email_notifier_with_invalid_credentials(self):
        self.assertRaises(ValueError,
                          self.check_simple_logger,
                          "<eventlog>\n"
                          "  <email-notifier>\n"
                          "    to sysadmin@example.com\n"
                          "    from zlog-user@example.com\n"
                          "    level fatal\n"
                          "    smtp-username john\n"
                          "  </email-notifier>\n"
                          "</eventlog>")
        self.assertRaises(ValueError,
                          self.check_simple_logger,
                          "<eventlog>\n"
                          "  <email-notifier>\n"
                          "    to sysadmin@example.com\n"
                          "    from zlog-user@example.com\n"
                          "    level fatal\n"
                          "    smtp-password john\n"
                          "  </email-notifier>\n"
                          "</eventlog>")

    def check_simple_logger_factory(self, text, level=logging.INFO):
        conf = self.get_config(text)
        self.assertTrue(conf.eventlog is not None)
        self.assertEqual(conf.eventlog.level, level)
        return conf.eventlog

    def check_simple_logger(self, text, level=logging.INFO):
        logger = self.check_simple_logger_factory(text, level)()
        self.assertTrue(isinstance(logger, logging.Logger))
        self.assertEqual(len(logger.handlers), 1)
        return logger


if os.name == 'nt':
    # Though log files can be closed and re-opened on Windows, these
    # tests expect to be able to move the underlying files out from
    # underneath the logger while open.  That's not possible on
    # Windows. So we don't extend TestCase so that they don't get run.
    #
    # Different tests are needed that only test that close/re-open
    # operations are performed by the handler; those can be run on
    # any platform.
    _RotateTestBase = object
else:
    _RotateTestBase = unittest.TestCase


class TestReopeningRotatingLogfiles(LoggingTestHelper, _RotateTestBase):

    # These tests should not be run on Windows.

    handler_factory = loghandler.RotatingFileHandler

    _schematext = """
      <schema>
        <import package='ZConfig.components.logger'/>
        <multisection type='logger' name='*' attribute='loggers'/>
      </schema>
    """

    _sampleconfig_template = """
      <logger>
        name  foo.bar
        <logfile>
          path  %(path0)s
          level debug
          max-size 1mb
          old-files 10
        </logfile>
        <logfile>
          path  %(path1)s
          level info
          max-size 1mb
          old-files 3
        </logfile>
        <logfile>
          path  %(path1)s
          level info
          when D
          old-files 3
        </logfile>
      </logger>

      <logger>
        name  bar.foo
        <logfile>
          path  %(path2)s
          level info
          max-size 10mb
          old-files 10
        </logfile>
      </logger>
    """

    def test_filehandler_reopen(self):

        def mkrecord(msg):
            args = ["foo.bar", logging.ERROR, __file__, 42, msg, (), ()]
            return logging.LogRecord(*args)

        # This goes through the reopening operation *twice* to make
        # sure that we don't lose our handle on the handler the first
        # time around.

        fn = self.mktemp()
        h = self.handler_factory(fn)
        h.handle(mkrecord("message 1"))
        nfn1 = self.move(fn)
        h.handle(mkrecord("message 2"))
        h.reopen()
        h.handle(mkrecord("message 3"))
        nfn2 = self.move(fn)
        h.handle(mkrecord("message 4"))
        h.reopen()
        h.handle(mkrecord("message 5"))
        h.close()

        # Check that the messages are in the right files::
        text1 = read_file(nfn1)
        text2 = read_file(nfn2)
        text3 = read_file(fn)
        self.assertTrue("message 1" in text1)
        self.assertTrue("message 2" in text1)
        self.assertTrue("message 3" in text2)
        self.assertTrue("message 4" in text2)
        self.assertTrue("message 5" in text3)

    def test_logfile_reopening(self):
        #
        # This test only applies to the simple logfile reopening; it
        # doesn't work the same way as the rotating logfile handler.
        #
        paths = self.mktemp(), self.mktemp(), self.mktemp()
        d = {
            "path0": paths[0],
            "path1": paths[1],
            "path2": paths[2],
            }
        text = self._sampleconfig_template % d
        conf = self.get_config(text)
        self.assertEqual(len(conf.loggers), 2)
        # Build the loggers from the configuration, and write to them:
        conf.loggers[0]().info("message 1")
        conf.loggers[1]().info("message 2")
        #
        # We expect this to re-open the original filenames, so we'll
        # have six files instead of three.
        #
        loghandler.reopenFiles()
        #
        # Write to them again:
        conf.loggers[0]().info("message 3")
        conf.loggers[1]().info("message 4")
        #
        # We expect this to re-open the original filenames, so we'll
        # have nine files instead of six.
        #
        loghandler.reopenFiles()
        #
        # Write to them again:
        conf.loggers[0]().info("message 5")
        conf.loggers[1]().info("message 6")
        #
        # We should now have all nine files:
        for fn in paths:
            fn1 = fn + ".1"
            fn2 = fn + ".2"
            self.assertTrue(os.path.isfile(fn), "%r must exist" % fn)
            self.assertTrue(os.path.isfile(fn1), "%r must exist" % fn1)
            self.assertTrue(os.path.isfile(fn2), "%r must exist" % fn2)
        #
        # Clean up:
        for logger in conf.loggers:
            logger = logger()
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()


class TestReopeningLogfiles(TestReopeningRotatingLogfiles):

    handler_factory = loghandler.FileHandler

    _sampleconfig_template = """
      <logger>
        name  foo.bar
        <logfile>
          path  %(path0)s
          level debug
        </logfile>
        <logfile>
          path  %(path1)s
          level info
        </logfile>
      </logger>

      <logger>
        name  bar.foo
        <logfile>
          path  %(path2)s
          level info
        </logfile>
      </logger>
    """

    def test_logfile_reopening(self):
        #
        # This test only applies to the simple logfile reopening; it
        # doesn't work the same way as the rotating logfile handler.
        #
        paths = self.mktemp(), self.mktemp(), self.mktemp()
        d = {
            "path0": paths[0],
            "path1": paths[1],
            "path2": paths[2],
            }
        text = self._sampleconfig_template % d
        conf = self.get_config(text)
        self.assertEqual(len(conf.loggers), 2)
        # Build the loggers from the configuration, and write to them:
        conf.loggers[0]().info("message 1")
        conf.loggers[1]().info("message 2")
        npaths1 = [self.move(fn) for fn in paths]
        #
        # We expect this to re-open the original filenames, so we'll
        # have six files instead of three.
        #
        loghandler.reopenFiles()
        #
        # Write to them again:
        conf.loggers[0]().info("message 3")
        conf.loggers[1]().info("message 4")
        npaths2 = [self.move(fn) for fn in paths]
        #
        # We expect this to re-open the original filenames, so we'll
        # have nine files instead of six.
        #
        loghandler.reopenFiles()
        #
        # Write to them again:
        conf.loggers[0]().info("message 5")
        conf.loggers[1]().info("message 6")
        #
        # We should now have all nine files:
        for fn in paths:
            self.assertTrue(os.path.isfile(fn), "%r must exist" % fn)
        for fn in npaths1:
            self.assertTrue(os.path.isfile(fn), "%r must exist" % fn)
        for fn in npaths2:
            self.assertTrue(os.path.isfile(fn), "%r must exist" % fn)
        #
        # Clean up:
        for logger in conf.loggers:
            logger = logger()
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()

    def test_filehandler_reopen_thread_safety(self):
        # The reopen method needs to do locking to avoid a race condition
        # with emit calls. For simplicity we replace the "acquire" and
        # "release" methods with dummies that record calls to them.

        fn = self.mktemp()
        h = self.handler_factory(fn)

        calls = []
        h.acquire = lambda: calls.append("acquire")
        h.release = lambda: calls.append("release")

        h.reopen()
        h.close()

        self.assertEqual(calls, ["acquire", "release"])

class TestFunctions(unittest.TestCase):

    def test_log_format_bad(self):
        self.assertRaisesRegexp(ValueError,
                                "Invalid log format string",
                                handlers.log_format,
                                "%{no-such-key}s")

    def test_resolve_deep(self):
        old_mod = None
        if hasattr(logging, 'handlers'):
            # This module is nested so it hits our coverage target,
            # and it doesn't alter any state
            # on import, so a "reimport" is fine
            del logging.handlers
            old_mod = sys.modules['logging.handlers']
            del sys.modules['logging.handlers']
        try:
            handlers.resolve('logging.handlers')
        finally:
            if old_mod is not None:
                logging.handlers = old_mod
                sys.modules['logging.handlers'] = old_mod

    def test_http_handler_url(self):
        self.assertRaisesRegexp(ValueError,
                                'must be an http',
                                handlers.http_handler_url, 'file://foo/baz')
        self.assertRaisesRegexp(ValueError,
                                'must specify a location',
                                handlers.http_handler_url, 'http://')
        self.assertRaisesRegexp(ValueError,
                                'must specify a path',
                                handlers.http_handler_url, 'http://server')

        v = handlers.http_handler_url("http://server/path;param?q=v#fragment")
        self.assertEqual(v, ('server', '/path;param?q=v#fragment'))

    def test_close_files(self):
        class F(object):
            closed = 0
            def close(self):
                self.closed += 1
        f = F()
        def wr():
            return f

        loghandler._reopenable_handlers.append(wr)
        loghandler.closeFiles()
        loghandler.closeFiles()

        self.assertEqual(1, f.closed)

    def test_reopen_files_missing_wref(self):
        # simulate concurrent iteration that pops the ref
        def wr():
            loghandler._reopenable_handlers.remove(wr)

        loghandler._reopenable_handlers.append(wr)
        loghandler.reopenFiles()

    def test_logging_level(self):
        # Make sure the expected names are supported; it's not clear
        # how to check the values in a meaningful way.
        # Just make sure they're case-insensitive.
        convert = datatypes.logging_level
        for name in ["notset", "all", "trace", "debug", "blather",
                     "info", "warn", "warning", "error", "fatal",
                     "critical"]:
            self.assertEqual(convert(name), convert(name.upper()))
        self.assertRaises(ValueError, convert, "hopefully-not-a-valid-value")
        self.assertEqual(convert('10'), 10)
        self.assertRaises(ValueError, convert, '100')

    def test_http_method(self):
        convert = handlers.get_or_post
        self.assertEqual(convert("get"), "GET")
        self.assertEqual(convert("GET"), "GET")
        self.assertEqual(convert("post"), "POST")
        self.assertEqual(convert("POST"), "POST")
        self.assertRaises(ValueError, convert, "")
        self.assertRaises(ValueError, convert, "foo")

    def test_syslog_facility(self):
        convert = handlers.syslog_facility
        for name in ["auth", "authpriv", "cron", "daemon", "kern",
                     "lpr", "mail", "news", "security", "syslog",
                     "user", "uucp", "local0", "local1", "local2",
                     "local3", "local4", "local5", "local6", "local7"]:
            self.assertEqual(convert(name), name)
            self.assertEqual(convert(name.upper()), name)
        self.assertRaises(ValueError, convert, "hopefully-never-a-valid-value")


class TestStartupHandler(unittest.TestCase):

    def test_buffer(self):
        handler = loghandler.StartupHandler()
        self.assertFalse(handler.shouldFlush(None))
        self.assertEqual(maxsize, handler.capacity)

        records = []
        def handle(record):
            records.append(record)
        handle.handle = handle

        handler.flushBufferTo(handle)
        self.assertEqual([], records)

        handler.buffer.append(1)
        handler.flushBufferTo(handle)
        self.assertEqual([1], records)

        del handle.handle

def test_logger_convenience_function_and_ommiting_name_to_get_root_logger():
    """

The ZConfig.loggers function can be used to configure one or more loggers.
We'll configure the rot logger and a non-root logger.

    >>> old_level = logging.getLogger().getEffectiveLevel()
    >>> old_handler_count = len(logging.getLogger().handlers)

    >>> ZConfig.configureLoggers('''
    ... <logger>
    ...    level INFO
    ...    <logfile>
    ...       PATH STDOUT
    ...       format root %(levelname)s %(name)s %(message)s
    ...    </logfile>
    ... </logger>
    ...
    ... <logger>
    ...    name ZConfig.TEST
    ...    level DEBUG
    ...    <logfile>
    ...       PATH STDOUT
    ...       format test %(levelname)s %(name)s %(message)s
    ...    </logfile>
    ... </logger>
    ... ''')

    >>> logging.getLogger('ZConfig.TEST').debug('test message')
    test DEBUG ZConfig.TEST test message
    root DEBUG ZConfig.TEST test message

    >>> logging.getLogger().getEffectiveLevel() == logging.INFO
    True
    >>> len(logging.getLogger().handlers) == old_handler_count + 1
    True
    >>> logging.getLogger('ZConfig.TEST').getEffectiveLevel() == logging.DEBUG
    True
    >>> len(logging.getLogger('ZConfig.TEST').handlers) == 1
    True

.. cleanup

    >>> logging.getLogger('ZConfig.TEST').setLevel(logging.NOTSET)
    >>> logging.getLogger('ZConfig.TEST').removeHandler(
    ...     logging.getLogger('ZConfig.TEST').handlers[-1])
    >>> logging.getLogger().setLevel(old_level)
    >>> logging.getLogger().removeHandler(logging.getLogger().handlers[-1])


    """

def test_suite():
    return unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromName(__name__),
        doctest.DocTestSuite()
    ])

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
