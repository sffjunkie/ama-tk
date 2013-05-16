
.. _Validation:

Validation
----------

.. _basic_types:
   
Types
~~~~~

The types available are "str", "bool", "int", "float"

Custom Types
~~~~~~~~~~~~

The custom validation types currently defined are

``yesno``
    matches one of ``yes``, ``y``, ``no``, ``n`` with any
    case plus True and False

:samp:`re({regex})`
    Verifies that the value specified matches the regular expression given
    between the brackets
    
``path``
    Verifies that the path specified exists.

``path(empty)``
    Verifies that the path specified exists and is empty.

``path(nonempty)``
    Verifies that the path specified exists and contains at least on file.
    
:samp:`path({pathspec})`
    Verifies that the path specified exists and conforms to the pathspec given
    (:ref:`see below <path_spec>`)

:samp:`date({datespec})`
    Verifies that the date is a valid date that matches the *datespec* where
    *datespec* follows the standard Python
    :meth:`~datetime.datetime.strptime`
    format string.
                           
:samp:`time({timespec})`
    Verifies that the time is a valid time that matches the *timespec* where
    *timespec* follows the standard Python
    :meth:`~datetime.datetime.strptime`
    format string. 

.. _path_spec:

Path Specs
~~~~~~~~~~

Path specs contain multiple glob patterns separated by commas each preceded by
either a plus or minus sign.

A plus sign (``+``) indicates that a file matching the glob must be in the
directory. 

A minus sign (``-``) indicates that a file matching the glob must not be in the
directory.

e.g. ``+test.py,-*.txt`` means the directory must have a :file:`test.py` file
included but no text files
