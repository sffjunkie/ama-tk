
.. _json_format:

Questions in JSON
-----------------

Each question is specified as an entry in a JSON dictionary.

After the dictionary key to use to lookup the question comes a list containing
the following...

* a short description/label to be displayed
* the type specified as a string "str", "bool" etc.
* the default value
* help text to display
* a custom type to validate against (see :ref:`Validation` below)

The default value can use Python
`string formatting <http://docs.python.org/library/string.html#format-examples>`_
operators to build a value from other answers as in the ``join_path`` question
below.

.. note::

   If you're using the terminal you can only refer to previous answers as the
   questions are asked in order of definition and only once.

JSON Example ::

   {
   "path":
      ["Root path",
        "str",
        ".",
        "Root path for the documentation",
        "path"
       ],
   "count":
      ["Number of items",
        "int",
        1,
        "How many items",
        null
       ],
   "payment":
      ["Payment per month",
        "float",
        1.1,
        "How many items",
        null
       ],
   "show_all":
      ["Show everything",
        "bool",
        true,
        "Do you want to show every single item in the whole world",
        null
       ],
   "show_yesno":
      ["Really everything",
        "bool",
        false,
        "Do you really want to show every single item in the whole world",
        "yesno"
       ],
   "something":
      ["A non empty field",
        "nonempty",
        "a",
        "You really have to enter something",
        null
       ],
   "path2":
       ["Another path",
        "str",
        "pypirc",
        "A second path used by the next question to join 2 together",
        null
       ],
   "join_path":
       ["Compound path",
        "str",
        "{path}/{path2}",
        "Joining of path & path2",
        "path"
       ]
   }
