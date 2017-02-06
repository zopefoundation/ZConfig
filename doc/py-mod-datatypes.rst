==================================================
 ZConfig.datatypes --- Default data type registry
==================================================

.. py:module:: ZConfig.datatypes
   :synopsis: Default implementation of a data type registry

The :mod:`ZConfig.datatypes` module provides the implementation of
the default data type registry and all the standard data types
supported by :mod:`ZConfig`.  A number of convenience classes are
also provided to assist in the creation of additional data types.

A "datatype registry" is an object that provides conversion
functions for data types.  The interface for a registry is fairly
simple.

A "conversion function" is any callable object that accepts a
single argument and returns a suitable value, or raises an exception
if the input value is not acceptable.  :exc:`ValueError` is the
preferred exception for disallowed inputs, but any other exception
will be properly propagated.

.. py:class:: Registry([stock])

  Implementation of a simple type registry.  If given, *stock*
  should be a mapping which defines the "built-in" data types for
  the registry; if omitted or ``None``, the standard set of data
  types is used (see :ref:`standard-datatypes`).



:class:`Registry` objects have the following methods:

.. py:method:: Registry.get(name)

  Return the type conversion routine for *name*.  If the
  conversion function cannot be found, an (unspecified) exception is
  raised.  If the name is not provided in the stock set of data types
  by this registry and has not otherwise been registered, this method
  uses the :meth:`search` method to load the conversion function.
  This is the only method the rest of :mod:`ZConfig` requires.


.. py:method:: Registry.register(name, conversion)

  Register the data type name *name* to use the conversion
  function *conversion*.  If *name* is already registered or
  provided as a stock data type, :exc:`ValueError` is raised
  (this includes the case when *name* was found using the
  :meth:`search` method).


.. py:method:: Registry.search(name)

  This is a helper method for the default implementation of the
  :meth:`get` method.  If *name* is a Python dotted-name, this
  method loads the value for the name by dynamically importing the
  containing module and extracting the value of the name.  The name
  must refer to a usable conversion function.



The following classes are provided to define conversion functions:

.. py:class:: MemoizedConversion(conversion)

  Simple memoization for potentially expensive conversions.  This
  conversion helper caches each successful conversion for re-use at a
  later time; failed conversions are not cached in any way, since it
  is difficult to raise a meaningful exception providing information
  about the specific failure.


.. py:class:: RangeCheckedConversion(conversion,[min [, max]])

  Helper that performs range checks on the result of another
  conversion.  Values passed to instances of this conversion are
  converted using *conversion* and then range checked.  *min*
  and *max*, if given and not ``None``, are the inclusive
  endpoints of the allowed range.  Values returned by *conversion*
  which lay outside the range described by *min* and *max*
  cause :exc:`ValueError` to be raised.


.. py:class:: RegularExpressionConversion(regex)

  Conversion that checks that the input matches the regular expression
  *regex*.  If it matches, returns the input, otherwise raises
  :exc:`ValueError`.
