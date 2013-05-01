
.. _Validation:

Validation
----------

.. _basic_types:
   
Types
~~~~~

The types available are "bool", "int", "float"

Custom Types
~~~~~~~~~~~~

The custom validation types currently defined are

:samp:`re({regex})`
    Verifies that the value specified matches the regular expression given
    between the brackets
    
`path`
    Verifies that the path specified exists.
    

`path(empty)`
    Verifies that the path specified exists and is empty.

`path(nonempty)`
    Verifies that the path specified exists and is contains at least on file.
    
:samp:`path({pathspec})`
    Verifies that the path specified exists and conforms to the pathspec given
    (see below)

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
