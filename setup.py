try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("README.rst") as f:
    README = f.read()
with open("CHANGES.rst") as f:
    CHANGES = f.read()


tests_require = [
    'docutils',
    'manuel',
    'zope.exceptions',
    'zope.testrunner',
]

setup(
    name="ZConfig",
    version='4.2',
    author="Fred L. Drake, Jr.",
    author_email="fred@fdrake.net",
    maintainer="Zope Foundation and Contributors",
    description="Structured Configuration Library",
    keywords=('configuration structured simple flexible typed hierarchy'
              ' logging'),
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
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'zconfig = ZConfig.validator:main',
            'zconfig_schema2html = ZConfig.schema2html:main',
        ],
        'pygments.lexers': [
            'zconfig = ZConfig.pygments:ZConfigLexer',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
    ],
    python_requires='>=3.9',
    extras_require={
        'test': tests_require,
        'docs': [
            'sphinx-rtd-theme',
            'sphinxcontrib-programoutput',
        ],
    },
)
