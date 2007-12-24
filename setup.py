from setuptools import find_packages, setup

README = open('README.txt').read()
NEWS = open('NEWS.txt').read()

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
    defaults = ['--test-path', here]
    options = get_options(args, defaults)
    suites = list(find_suites(options))
    return TestSuite(suites)

setup(
    name="ZConfig",
    version="2.5.2dev",
    author="Fred L. Drake, Jr.",
    author_email="fred@zope.com",
    description="Structured Configuration Library",
    long_description=README + '\n\n' + NEWS,
    license="ZPL 2.1",
    url='http://www.zope.org/Members/fdrake/zconfig/',

    packages=find_packages("."),
    scripts=["scripts/zconfig", "scripts/zconfig_schema2html"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
      'Intended Audience :: Developers',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: Zope Public License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],
    test_suite='__main__.alltests', # support 'setup.py test'
    tests_require=[
      'zope.testing',
    ]
    )
