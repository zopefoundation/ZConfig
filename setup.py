try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("README.rst") as f:
    README = f.read()
with open("CHANGES.rst") as f:
    CHANGES = f.read()

def alltests():
    import os
    import sys
    import unittest
    # use the zope.testrunner machinery to find all the
    # test suites we've put under ourselves
    import zope.testrunner.find
    import zope.testrunner.options
    here = os.path.abspath(os.path.dirname(sys.argv[0]))
    args = sys.argv[:]
    defaults = ["--test-path", here]
    options = zope.testrunner.options.get_options(args, defaults)
    suites = list(zope.testrunner.find.find_suites(options))
    return unittest.TestSuite(suites)

tests_require = [
    'zope.testrunner',
]

options = dict(
    name="ZConfig",
    version='3.2.0.dev0',
    author="Fred L. Drake, Jr.",
    author_email="fred@fdrake.net",
    maintainer="Zope Foundation and Contributors",
    description="Structured Configuration Library",
    long_description=README + "\n\n" + CHANGES,
    license="ZPL 2.1",
    url="https://github.com/zopefoundation/ZConfig/",
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
    entry_points={
        'console_scripts': [
            'zconfig = ZConfig.validator:main',
            'zconfig_schema2html = ZConfig.schema2html:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Zope Public License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        ],
    # Support for 'setup.py test' when setuptools is available:
    test_suite='__main__.alltests',
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'docs': [
            'nti.sphinxcontrib-programoutput',
        ]
    },
)


setup(**options)
