"""Tests for <textblocktype> and <textblock>.

"""
__docformat__ = "reStructuredText"

import unittest

import ZConfig

from ZConfig.tests.support import TestBase, CONFIG_BASE


def uppercase(value):
    return str(value).upper()


class TextBlockTestCase(TestBase):
    """Tests of the text block support."""

    def test_simple(self):
        schema = self.load_schema_text("""\
            <schema>
              <textblocktype name='why'/>
              <textblock attribute='explanation' type='why'/>
            </schema>
            """)
        conf = self.load_config_text(schema, """\
            <why>
              Some long explanation goes here.
            </why>
            """)
        self.assertEqual(conf.explanation.strip(),
                         "Some long explanation goes here.")

    def test_with_datatype(self):
        schema = self.load_schema_text("""\
            <schema>
              <textblocktype name='why'
                             datatype='%s.uppercase'/>
              <textblock attribute='explanation' type='why'/>
            </schema>
            """ % __name__)
        conf = self.load_config_text(schema, """\
            <why>
              Some long explanation goes here.
            </why>
            """)
        self.assertEqual(conf.explanation.strip(),
                         "SOME LONG EXPLANATION GOES HERE.")

    def test_with_default(self):
        schema = self.load_schema_text("""\
            <schema>
              <textblocktype name='why'/>
              <textblock attribute='explanation' type='why'>
                <default>
                  default value
                </default>
              </textblock>
            </schema>
            """)
        conf = self.load_config_text(schema, "")
        self.assertEqual(conf.explanation.strip(), "default value")

    def test_named(self):
        schema = self.load_schema_text("""\
            <schema>
              <textblocktype name='why'/>
              <textblock attribute='explanation' required='yes'
                         type='why' name='not'/>
            </schema>
            """)
        conf = self.load_config_text(schema, """\
            <why not>
              Some long explanation goes here.
            </why>
            """)
        self.assertEqual(conf.explanation.strip(),
                         "Some long explanation goes here.")


def test_suite():
    return unittest.makeSuite(TextBlockTestCase)
