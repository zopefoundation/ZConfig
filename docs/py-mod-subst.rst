==============================================
 ZConfig.substitution --- String substitution
==============================================

.. automodule:: ZConfig.substitution

This module provides a basic substitution facility similar to that
found in the Bourne shell (``sh`` on most UNIX platforms).

The replacements supported by this module include:

=========== =================================================== =====
Source      Replacement                                         Notes
=========== =================================================== =====
``$$``      ``$``                                               (1)
``$name``   The result of looking up *name*                     (2)
``${name}`` The result of looking up *name*
``$(name)`` The result of looking up *name*  in the environment (3)
=========== =================================================== =====

Notes:

1.  This is different from the Bourne shell, which uses
    ``\$`` to generate a ``$`` in
    the result text.  This difference avoids having as many
    special characters in the syntax.

2.  Any character which immediately follows *name* may
    not be a valid character in a name.

3. This is not Bourne shell style.

In each case, *name* is a non-empty sequence of alphanumeric and
underscore characters not starting with a digit.  If there is not a
replacement for *name*, the exception
:exc:`~.SubstitutionReplacementError` is raised.
Note that the lookup is expected to be case-insensitive; this module
will always use a lower-case version of the name to perform the query.

This module provides these functions:

.. autofunction:: substitute


.. autofunction:: isname


Examples
========

.. highlight:: pycon

::

  >>> from ZConfig.substitution import substitute
  >>> d = {'name': 'value',
  ...      'top': '$middle',
  ...      'middle' : 'bottom'}
  >>>
  >>> substitute('$name', d)
  'value'
  >>> substitute('$top', d)
  '$middle'
  >>> import os
  >>> os.environ['from_environment'] = 'From environment.'
  >>> substitute('$(from_einvironment)', d)
  'From environment.'
  