==============================================
 ZConfig.substitution --- String substitution
==============================================

.. py:module:: ZConfig.substitution
  :synopsis: Shell-style string substitution helper.

This module provides a basic substitution facility similar to that
found in the Bourne shell (``sh`` on most UNIX platforms).

The replacements supported by this module include:

=========== ================================ =====
Source      Replacement                      Notes
=========== ================================ =====
``$$``      ``$``                            (1)
``$name``   The result of looking up *name*  (2)
``${name}`` The result of looking up *name*
=========== ================================ =====

Notes:

1.  This is different from the Bourne shell, which uses
    ``\$`` to generate a ``$`` in
    the result text.  This difference avoids having as many
    special characters in the syntax.

2.  Any character which immediately follows *name* may
    not be a valid character in a name.


In each case, *name* is a non-empty sequence of alphanumeric and
underscore characters not starting with a digit.  If there is not a
replacement for *name*, the exception
:exc:`~.SubstitutionReplacementError` is raised.
Note that the lookup is expected to be case-insensitive; this module
will always use a lower-case version of the name to perform the query.

This module provides these functions:

.. py:function:: substitute(s, mapping)

  Substitute values from *mapping* into *s*.  *mapping*
  can be a :class:`dict` or any type that supports the ``get()``
  method of the mapping protocol.  Replacement
  values are copied into the result without further interpretation.
  Raises :exc:`~.SubstitutionSyntaxError` if there are malformed
  constructs in *s*.



.. py:function:: isname(s)

  Returns ``True`` if *s* is a valid name for a substitution
  text, otherwise returns ``False``.



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
