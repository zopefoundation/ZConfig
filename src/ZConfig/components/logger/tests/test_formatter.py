# coding=utf-8
##############################################################################
#
# Copyright (c) 2018 Zope Foundation and Contributors.
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
"""\
Tests for ZConfig.components.logger.formatter.

"""

import logging
import sys
import unittest

import ZConfig.components.logger.formatter
import ZConfig.components.logger.tests.support


# In Python 3.8, a KeyError raised by string interpolation is re-written
# into a ValueError reporting a reference to an undefined field.  We're
# not masking the exception, but we want to check for the right one in
# the tests below (without catching anything else).
#
if sys.version_info >= (3, 8):
    MissingFieldError = ValueError
else:
    MissingFieldError = KeyError


class LogFormatStyleTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.convert = ZConfig.components.logger.formatter.log_format_style

    def test_classic(self):
        self.assertEqual(self.convert('classic'), 'classic')
        self.assertEqual(self.convert('Classic'), 'classic')
        self.assertEqual(self.convert('CLASSIC'), 'classic')
        self.assertEqual(self.convert('cLaSsIc'), 'classic')

    def test_format(self):
        self.assertEqual(self.convert('format'), 'format')
        self.assertEqual(self.convert('Format'), 'format')
        self.assertEqual(self.convert('FORMAT'), 'format')
        self.assertEqual(self.convert('fOrMaT'), 'format')

    def test_template(self):
        self.assertEqual(self.convert('template'), 'template')
        self.assertEqual(self.convert('Template'), 'template')
        self.assertEqual(self.convert('TEMPLATE'), 'template')
        self.assertEqual(self.convert('tEmPlAtE'), 'template')

    def test_safe_template(self):
        self.assertEqual(self.convert('safe-template'), 'safe-template')
        self.assertEqual(self.convert('Safe-Template'), 'safe-template')
        self.assertEqual(self.convert('SAFE-TEMPLATE'), 'safe-template')
        self.assertEqual(self.convert('sAfE-tEmPlAtE'), 'safe-template')

    def test_bad_values(self):

        def check(value):
            with self.assertRaises(ValueError) as cm:
                self.convert(value)
            self.assertIn('log_format_style must be one of',
                          str(cm.exception))
            self.assertIn('found %r' % value, str(cm.exception))

        check('')
        check('just-some-junk')
        check('Another Pile of Junk')
        check('%')
        check('{')
        check('$')


class StyledFormatterTestHelper(
        ZConfig.components.logger.tests.support.LoggingTestHelper):

    _schematext = """
      <schema>
        <import package='ZConfig.components.logger'/>
        <section type='eventlog' name='*' attribute='eventlog'/>
      </schema>
    """

    _config_template = """\
      <eventlog>
        <logfile>
          path STDOUT
          level debug
          %s
        </logfile>
      </eventlog>
    """

    def setUp(self):
        ZConfig.components.logger.tests.support.LoggingTestHelper.setUp(self)
        self.record = logging.LogRecord(
            'ZConfig.foo.bar', logging.WARN, __file__, 42,
            'my message, %r %r', ('with', 'some args'), None, 'faux_func')
        self.record.x1 = 24
        self.record.x2 = 37

    def get_logger_factory(self, style=None, format=None,
                           arbitrary_fields=False):
        formatter_lines = []
        if style:
            formatter_lines.append('style %s' % style)
        if format:
            formatter_lines.append('format %s' % format)
        if arbitrary_fields:
            formatter_lines.append('arbitrary-fields true')
        formatter_config = '\n    '.join(formatter_lines)
        parsed = self.get_config(self._config_template % formatter_config)
        return parsed.eventlog

    def get_formatter_factory(self, style=None, format=None,
                              arbitrary_fields=False):
        logger_factory = self.get_logger_factory(
            style=style, format=format, arbitrary_fields=arbitrary_fields)
        return logger_factory.handler_factories[0].create_formatter

    def get_formatter(self, style=None, format=None, arbitrary_fields=False):
        factory = self.get_formatter_factory(
            style=style, format=format, arbitrary_fields=arbitrary_fields)
        return factory()


class LoggerStyledFormatterTestCase(StyledFormatterTestHelper,
                                    unittest.TestCase):

    def test_classic_explicit(self):
        formatter = self.get_formatter(
            style='classic',
            format='%(levelname)s %(levelno)s %(message)s')
        content = formatter.format(self.record)
        self.assertEqual(content, "WARNING 30 my message, 'with' 'some args'")

    def test_classic_implicit(self):
        formatter = self.get_formatter(
            format='%(levelname)s %(levelno)s %(message)s')
        content = formatter.format(self.record)
        self.assertEqual(content, "WARNING 30 my message, 'with' 'some args'")

    def test_format(self):
        #
        # The last item here isn't a format string placeholder; it
        # almost looks like a classic format operation, but would cause
        # an error.  We're just expecting it to show up in the result as
        # a literal.
        #
        # It would not be allowed in older versions of ZConfig, or for
        # classic style.
        #
        formatter = self.get_formatter(
            style='format',
            format='{levelname} {levelno} {message} %(stuff)')
        content = formatter.format(self.record)
        self.assertEqual(
            content, "WARNING 30 my message, 'with' 'some args' %(stuff)")

    def test_format_with_anonymous_placeholders(self):
        with self.assertRaises(ValueError):
            self.get_formatter_factory(
                style='format',
                format='{} {} {} %(stuff)')

    def test_format_with_positional_placeholders(self):
        with self.assertRaises(ValueError):
            self.get_formatter_factory(
                style='format',
                format='{1} {2} {3} %(stuff)')

    # These comments apply to the test_template_* and
    # test_safe_template_* tests that demonstrate successful formatter
    # creations.
    #
    # The last item here isn't a format string placeholder; it almost
    # looks like a classic format operation, but would cause an error.
    # We're just expecting it to show up in the result as a literal.
    #
    # It would not be allowed in older versions of ZConfig, or for
    # classic style.
    #
    # Note the $ must be doubled to get through the ZConfig syntax for
    # substitutions.
    #
    def test_template_with_braces(self):
        formatter = self.get_formatter(
            style='template',
            format='$${levelname} $${levelno} $${message} %(stuff) {extra}')
        content = formatter.format(self.record)
        self.assertEqual(
            content, ("WARNING 30 my message, 'with' 'some args'"
                      " %(stuff) {extra}"))

    def test_template_without_braces(self):
        formatter = self.get_formatter(
            style='template',
            format='$$levelname $$levelno $$message %(stuff) {extra}')
        content = formatter.format(self.record)
        self.assertEqual(
            content, ("WARNING 30 my message, 'with' 'some args'"
                      " %(stuff) {extra}"))

    def test_template_with_junk(self):
        #
        # There's a lot of junk in this format; we're verifying that
        # it's caught when constructing the factory.
        #
        with self.assertRaises(ValueError):
            self.get_formatter_factory(
                style='format',
                format='$$} $${levelno')

    def test_safe_template_with_braces(self):
        formatter = self.get_formatter(
            style='safe-template',
            format='$${levelname} $${levelno} $${message} %(stuff) {extra}')
        content = formatter.format(self.record)
        self.assertEqual(
            content, ("WARNING 30 my message, 'with' 'some args'"
                      " %(stuff) {extra}"))

    def test_safe_template_without_braces(self):
        formatter = self.get_formatter(
            style='safe-template',
            format='$$levelname $$levelno $$message %(stuff) {extra}')
        content = formatter.format(self.record)
        self.assertEqual(
            content, ("WARNING 30 my message, 'with' 'some args'"
                      " %(stuff) {extra}"))

    def test_safe_template_with_junk(self):
        formatter = self.get_formatter(
            style='safe-template',
            format=('$${levelname} $${levelno} $${message} %(stuff) {extra}'
                    ' $$} $${levelno  $${bad-mojo}'))
        content = formatter.format(self.record)
        self.assertEqual(
            content, ("WARNING 30 my message, 'with' 'some args'"
                      " %(stuff) {extra} $} ${levelno  ${bad-mojo}"))


class ZopeExceptionsFormatterTestCase(LoggerStyledFormatterTestCase):

    # We test against the zope.exceptions formatter since it's a common
    # example of a formatter that inherits almost everything, but
    # defines it's own formatException.  For Python 2, we want to be
    # sure the extended formatException is used.

    _config_template = """\
      <eventlog>
        <logfile>
          path STDOUT
          level debug
          formatter zope.exceptions.log.Formatter
          %s
        </logfile>
      </eventlog>
    """

    def test_format_with_traceback_info(self):
        formatter = self.get_formatter(
            style='format',
            format='{levelname} {levelno} {message}')

        def fail():
            raise RuntimeError('foo')

        def something():
            __traceback_info__ = 42
            fail()

        try:
            something()
        except RuntimeError:
            self.record.exc_info = sys.exc_info()

        content = formatter.format(self.record)
        self.assertIn(' - __traceback_info__: 42', content)
        self.assertIn("WARNING 30 my message, 'with' 'some args'", content)


class CustomFormatterClassWithoutStyleParamTestCase(
        LoggerStyledFormatterTestCase):

    _config_template = """\
      <eventlog>
        <logfile>
          path STDOUT
          level debug
          formatter %s.StylelessFormatter
          %%s
        </logfile>
      </eventlog>
    """ % __name__


class CustomFormatterFactoryWithoutStyleParamTestCase(
        LoggerStyledFormatterTestCase):

    _config_template = """\
      <eventlog>
        <logfile>
          path STDOUT
          level debug
          formatter %s.styleless_formatter
          %%s
        </logfile>
      </eventlog>
    """ % __name__


class StylelessFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None):
        kwargs = dict()
        if sys.version_info >= (3, 8):
            kwargs['validate'] = False
        logging.Formatter.__init__(self, fmt=fmt, datefmt=datefmt, **kwargs)


def styleless_formatter(fmt=None, datefmt=None):
    return StylelessFormatter(fmt=fmt, datefmt=datefmt)


class UnstylableFormatter(StylelessFormatter):

    # Really only declared unstylable on Python 2; Python 3 formatters
    # are assumed to be cooperative w/r/t format invoking formatMessage.

    def format(self, record):
        return 'No playing nice!'


class UnstylableFormatterTestCase(StyledFormatterTestHelper,
                                  unittest.TestCase):

    _config_template = """\
      <eventlog>
        <logfile>
          path STDOUT
          level debug
          formatter %s.UnstylableFormatter
          %%s
        </logfile>
      </eventlog>
    """ % __name__

    @unittest.skipIf(sys.version_info[0] > 2,
                     'Only applies for Python 2.')
    def test_py2_unstylable(self):
        factory = self.get_formatter_factory(
            style='template',
            format='$${levelname} $${levelno} $${message}')
        with self.assertRaises(ValueError) as cm:
            factory()
        self.assertIn('cannot inject non-classic formatting into formatter',
                      str(cm.exception))


class Py2EncodingTestCase(StyledFormatterTestHelper,
                          unittest.TestCase):

    text = u'\u6d4b\u8bd5'  # u'测试'
    encoded_text = text.encode('utf-8')

    @unittest.skipIf(sys.version_info[0] > 2,
                     'Only applies for Python 2.')
    def test_format_message_with_unhandlable_unicode_decoding_error(self):
        # Triggering outer exception handler in Py2Formatter.formatMessage.
        formatter = ZConfig.components.logger.formatter.Py2Formatter(
            '%(name)s %(message)s ' + self.encoded_text)
        self.record.message = u'simple text'

        # Because the decoding error is caused by the unicode message,
        # decoding the nsame of the logger doesn't help:
        with self.assertRaises(UnicodeDecodeError) as cm:
            formatter.formatMessage(self.record)

        emsg = str(cm.exception)
        self.assertIn("'ascii' codec can't decode byte", emsg)
        self.assertIn('ordinal not in range(128)', emsg)

    @unittest.skipIf(sys.version_info[0] > 2,
                     'Only applies for Python 2.')
    def _test_format_message_with_unicode_logger_name(self):
        # https://bugs.python.org/issue25664
        logname = __name__ + '.' + self.encoded_text
        assert isinstance(logname, bytes)
        self.record.name = logname
        formatter = ZConfig.components.logger.formatter.Py2Formatter(
            '%(name)s %(message)s')
        self.record.message = self.record.getMessage()

        msg = formatter.formatMessage(self.record)

        self.assertIsInstance(msg, bytes)
        self.assertEqual(msg, logname + b" my message, 'with' 'some args'")

    @unittest.skipIf(sys.version_info[0] > 2,
                     'Only applies for Python 2.')
    def test_format_with_unicode_traceback_content(self):
        try:
            raise RuntimeError('we made this up')
        except RuntimeError:
            self.record.exc_info = sys.exc_info()
        formatter = ZConfig.components.logger.formatter.Py2Formatter(
            '%(name)s %(message)s')
        # For formatMessage to return unicode:
        self.record.msg += u''
        formatter.format(self.record)
        assert isinstance(self.record.exc_text, bytes)
        assert isinstance(formatter.formatMessage(self.record), unicode)  # NOQA
        # We're now certain self.record.exc_text has been properly formatted.
        # Convert to unicode and add some interesting bits.
        encoded_text = self.text.encode(sys.getfilesystemencoding())
        self.record.exc_text = (self.record.exc_text + encoded_text)
        self.record.message = self.record.message.decode('utf-8')

        msg = formatter.format(self.record)

        self.assertIsInstance(msg, unicode)  # NOQA

    @unittest.skipIf(sys.version_info[0] > 2,
                     'Only applies for Python 2.')
    def test_format_with_unicode_traceback_content_trailing_msg_newline(self):
        # The point of this is to cover the case of *not* adding a
        # newline to the message before appending the formatted
        # traceback.
        try:
            raise RuntimeError('we made this up')
        except RuntimeError:
            self.record.exc_info = sys.exc_info()
        formatter = ZConfig.components.logger.formatter.Py2Formatter(
            '%(name)s %(message)s')
        # For formatMessage to return unicode:
        self.record.msg += u'\n'
        formatter.format(self.record)
        assert isinstance(self.record.exc_text, bytes)
        assert isinstance(formatter.formatMessage(self.record), unicode)  # NOQA
        # We're now certain self.record.exc_text has been properly formatted.
        # Convert to unicode and add some interesting bits.
        encoded_text = self.text.encode(sys.getfilesystemencoding())
        self.record.exc_text = (self.record.exc_text + encoded_text)
        self.record.message = self.record.message.decode('utf-8')

        msg = formatter.format(self.record)

        self.assertIsInstance(msg, unicode)  # NOQA


class FieldTypesTestCase(StyledFormatterTestHelper, unittest.TestCase):

    def test_func_name_classic(self):
        formatter = self.get_formatter(
            style='classic',
            format='%(levelname)s %(levelno)2d %(funcName)s')
        output = formatter.format(self.record)
        self.assertIn('WARNING 30 faux_func', output)

    def test_func_name_format(self):
        formatter = self.get_formatter(
            style='format',
            format='{levelname} {levelno:02d} {funcName}')
        output = formatter.format(self.record)
        self.assertIn('WARNING 30 faux_func', output)

    def test_func_name_template(self):
        formatter = self.get_formatter(
            style='template',
            format='$$levelname $$levelno $$funcName')
        output = formatter.format(self.record)
        self.assertIn('WARNING 30 faux_func', output)

    def test_levelno_integer_classic(self):
        formatter = self.get_formatter(
            style='classic',
            format='%(levelname)s %(levelno)2d %(message)s')
        output = formatter.format(self.record)
        self.assertIn('WARNING 30 my message', output)

    def test_levelno_integer_format(self):
        formatter = self.get_formatter(
            style='format',
            format='{levelname} {levelno:02d} {message}')
        output = formatter.format(self.record)
        self.assertIn('WARNING 30 my message', output)

    def test_msecs_float_classic(self):
        formatter = self.get_formatter(
            style='classic',
            format='%(asctime)s.%(msecs)03.0f %(levelname)s %(message)s')
        self.record.msecs = 619.041919708252
        output = formatter.format(self.record)
        expected = '%s.619 WARNING my message' % self.record.asctime
        self.assertIn(expected, output)

    def test_msecs_float_format(self):
        formatter = self.get_formatter(
            style='format',
            format='{asctime}.{msecs:03.0f} {levelname} {message}')
        self.record.msecs = 619.041919708252
        output = formatter.format(self.record)
        expected = '%s.619 WARNING my message' % self.record.asctime
        self.assertIn(expected, output)

    def test_relative_created_float_classic(self):
        formatter = self.get_formatter(
            style='classic',
            format='%(relativeCreated)+.3f %(levelname)s %(message)s')
        self.record.relativeCreated = 406.7840576171875
        output = formatter.format(self.record)
        self.assertIn('+406.784 WARNING my message', output)

    def test_relative_created_float_format(self):
        formatter = self.get_formatter(
            style='format',
            format='{relativeCreated:+.3f} {levelname} {message}')
        self.record.relativeCreated = 406.7840576171875
        output = formatter.format(self.record)
        self.assertIn('+406.784 WARNING my message', output)


class ArbitraryFieldsTestCase(StyledFormatterTestHelper, unittest.TestCase):

    def test_classic_arbitrary_field_disallowed_by_default(self):
        with self.assertRaises(KeyError) as cm:
            self.get_formatter_factory(
                style='classic',
                format='%(levelno)s %(levelname)s %(undefined_field)s')
        self.assertEqual(str(cm.exception), "'undefined_field'")

    def test_format_arbitrary_field_disallowed_by_default(self):
        with self.assertRaises(KeyError) as cm:
            self.get_formatter_factory(
                style='format',
                format='{levelno} {levelname} {undefined_field}')
        self.assertEqual(str(cm.exception), "'undefined_field'")

    def test_template_arbitrary_field_disallowed_by_default(self):
        with self.assertRaises(KeyError) as cm:
            self.get_formatter_factory(
                style='format',
                format='$${levelno} $${levelname} $${undefined_field}')
        self.assertEqual(str(cm.exception), "'undefined_field'")

    # We don't need to check the safe-template variety, because it's
    # highly permissive.

    def test_classic_arbitrary_field_missing(self):
        formatter = self.get_formatter(
            style='classic',
            format='%(levelno)s %(levelname)s %(undefined_field)s',
            arbitrary_fields=True)

        # The formatter still breaks when it references an undefined field:
        with self.assertRaises(MissingFieldError) as cm:
            formatter.format(self.record)
        self.assertIn("'undefined_field'", str(cm.exception))

    def test_classic_arbitrary_field_present(self):
        formatter = self.get_formatter(
            style='classic',
            format='%(levelno)s %(levelname)s %(undefined_field)s',
            arbitrary_fields=True)

        # Given the field, it formats just fine:
        self.record.undefined_field = 'surprise!'
        logentry = formatter.format(self.record)
        self.assertIn('surprise!', logentry)

    def test_format_arbitrary_field_missing(self):
        formatter = self.get_formatter(
            style='format',
            format='{levelno} {levelname} {undefined_field}',
            arbitrary_fields=True)

        # The formatter still breaks when it references an undefined field:
        with self.assertRaises(MissingFieldError) as cm:
            formatter.format(self.record)
        self.assertIn("'undefined_field'", str(cm.exception))

    def test_format_arbitrary_field_present(self):
        formatter = self.get_formatter(
            style='format',
            format='{levelno} {levelname} {undefined_field}',
            arbitrary_fields=True)

        # Given the field, it formats just fine:
        self.record.undefined_field = 'surprise!'
        logentry = formatter.format(self.record)
        self.assertIn('surprise!', logentry)

    def test_template_arbitrary_field_missing(self):
        formatter = self.get_formatter(
            style='template',
            format='$${levelno} $${levelname} $${undefined_field}',
            arbitrary_fields=True)

        # The formatter still breaks when it references an undefined field:
        with self.assertRaises(MissingFieldError) as cm:
            formatter.format(self.record)
        self.assertIn("'undefined_field'", str(cm.exception))

    def test_template_arbitrary_field_present(self):
        formatter = self.get_formatter(
            style='template',
            format='$${levelno} $${levelname} $${undefined_field}',
            arbitrary_fields=True)

        # Given the field, it formats just fine:
        self.record.undefined_field = 'surprise!'
        logentry = formatter.format(self.record)
        self.assertIn('surprise!', logentry)

    def test_safe_template_arbitrary_field_missing(self):
        formatter = self.get_formatter(
            style='safe-template',
            format='$${levelno} $${levelname} $${undefined_field}',
            arbitrary_fields=True)

        # The formatter still breaks when it references an undefined field:
        logentry = formatter.format(self.record)
        self.assertIn(' ${undefined_field}', logentry)

    def test_safe_template_arbitrary_field_present(self):
        formatter = self.get_formatter(
            style='safe-template',
            format='$${levelno} $${levelname} $${undefined_field}',
            arbitrary_fields=True)

        # Given the field, it formats just fine:
        self.record.undefined_field = 'surprise!'
        logentry = formatter.format(self.record)
        self.assertIn('surprise!', logentry)
