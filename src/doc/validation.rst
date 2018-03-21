.. Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

.. _Validation:

Validation
----------

.. _basic_types:

Types
~~~~~

The types available are

   * nonempty
   * str
   * bool
   * yesno (like bool but displays " (y/n)" at the prompt)
   * int
   * float
   * path
   * date
   * time
   * color (RGB and RGB Hex e.g. rgb(1.0, 0.0, 0.0) or #ff0000 for red)
   * regular expressions
   * An entry point definition

``nonempty``
    Enter any value to pass the validation.

``bool``
    Matches any of ``true``, ``false``, ``1``, ``0``\.

``yesno``
    Matches any of ``yes``, ``y``, ``no``, ``n`` with any
    case plus the ``bool`` values

``str``
    Can it be converted to a string.

``int``
    Can it be converted to an integer.

``float``
    Can it be converted to a float.

``path``
    Verifies that the value is a valid path. Varoius specs can be provided to
    modify the path validation

    ``empty``
        verifies that the path is empty

    ``nonempty``
        verifies that at least one file is found in the path

    ``new``
        verifies that the path does not exist and is a valid path name

    :samp:`{pathspec}`
        Verifies that the path conforms to the :samp:`{pathspec}` given
        (:ref:`see below <path_spec>`)

``date``
    Verifies that a valid date is provided that matches the *datespec* where
    *datespec* follows the standard Python :meth:`~datetime.datetime.strptime`
    format string. If no specification is provided then ``%Y-%m-%d`` will be used.

``time``
    Verifies that the time is a valid time that matches the *timespec* where
    *timespec* follows the standard Python :meth:`~datetime.datetime.strptime`
    format string. If no specification is provided then ``%H:%M`` will be used.

``color``
    Verifies that the value is a valid color that matches the *colorspec* where
    *colorspec* is either ``rgb`` or ``rgbhex``

``re``
    Verifies that the value specified matches the regular expression.

Entry Point
    If a setuptools entry point is specified then it will be loaded and used
    to validate the entry.

.. _path_spec:

Path Specs
~~~~~~~~~~

Path specs contain multiple :mod:`glob` patterns separated by commas each
preceded by either a plus or minus sign.

A plus sign (``+``) indicates that a file matching the glob must be in the
directory.

A minus sign (``-``) indicates that a file matching the glob must not be in the
directory.

e.g. ``+test.py,-*.txt`` means the directory must have a :file:`test.py` file
included but no text files
