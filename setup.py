README = open("README.txt").read()
NEWS = open("NEWS.txt").read()

def alltests():
    import os
    import sys
    from unittest import TestSuite
    # use the zope.testing testrunner machinery to find all the
    # test suites we've put under ourselves
    from zope.testing.testrunner import get_options
    from zope.testing.testrunner import find_suites
    from zope.testing.testrunner import configure_logging
    configure_logging()
    here = os.path.abspath(os.path.dirname(sys.argv[0]))
    args = sys.argv[:]
    defaults = ["--test-path", here]
    options = get_options(args, defaults)
    suites = list(find_suites(options))
    return TestSuite(suites)

options = dict(
    name="ZConfig",
    version="2.8.0",
    author="Fred L. Drake, Jr.",
    author_email="fred@zope.com",
    maintainer="Zope Foundation and Contributors",
    description="Structured Configuration Library",
    long_description=README + "\n\n" + NEWS,
    license="ZPL 2.1",
    url="http://www.zope.org/Members/fdrake/zconfig/",
    # List packages explicitly so we don't have to assume setuptools:
    packages=[
        "ZConfig",
        "ZConfig.components",
        "ZConfig.components.basic",
        "ZConfig.components.basic.tests",
        "ZConfig.components.logger",
        "ZConfig.components.logger.tests",
        "ZConfig.tests",
        "ZConfig.tests.library",
        "ZConfig.tests.library.thing",
        "ZConfig.tests.library.widget",
        ],
    scripts=["scripts/zconfig", "scripts/zconfig_schema2html"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    # Support for 'setup.py test' when setuptools is available:
    test_suite="__main__.alltests",
    tests_require=[
        "zope.testing",
        ],
    )

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(**options)
