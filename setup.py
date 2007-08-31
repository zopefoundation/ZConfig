from setuptools import find_packages, setup

setup(
    name="ZConfig",
    version="2.5.0",
    author="Fred L. Drake, Jr.",
    author_email="fred@zope.com",
    description="Structured Configuration Library",
    long_description=open("README.txt").read(),
    license="ZPL 2.1",
    url='http://www.zope.org/Members/fdrake/zconfig/',

    packages=find_packages("."),
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
    )
