from setuptools import setup
name = "ZConfig"

long_description = """\
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
"""

setup(
    name = name,
    version = "2.4a2",
    author = "Fred L. Drake, Jr.",
    author_email = "fred@zope.com",
    description = "Structured Configuration Library",
    long_description=long_description,
    license = "ZPL 2.1",
    url='http://www.zope.org/Members/fdrake/zconfig/',

    packages = ['ZConfig'],
    include_package_data = True,
    zip_safe=False,
    classifiers = [
      'Intended Audience :: Developers',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: Zope Public License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
      ],
    )
