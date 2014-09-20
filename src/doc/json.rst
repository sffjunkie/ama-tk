.. Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

.. _json_format:

Questions in JSON
-----------------

Each question is specified as an entry in a JSON dictionary.

After the dictionary key to use to lookup the question comes a list containing
the following...

* a short description/label to be displayed
* help text to display
* the default value
* the type specified as a string "str", "bool" etc.
* a custom specification to modify the validation (see :ref:`Validation`).

The default value can use Python
`string formatting <http://docs.python.org/library/string.html#format-examples>`_
operators to build a value from other answers as in the ``join_path`` question
below.

.. note::

   If you're using the terminal you can only refer to previous answers as the
   questions are asked in order of definition and only once.

JSON Example ::

   {
   "a_date":
       ["Select a date",
        "A date",
        null,
        "date",
        null
       ],
   "a_time":
       ["Select a time",
        "A time",
        null,
        "time",
        "%H:%M:%S"
       ],
   "a_color":
       ["Select a color",
        "A color",
        "#fdcbef",
        "color",
        "rgbhex"
       ],
   "path":
      ["Root path",
        "Root path for the documentation",
        ".",
        "path",
        "new"
       ],
   "count":
      ["Number of items",
        "How many items",
        1,
        "int",
        null
       ],
   "payment":
      ["Payment per month",
        "How many items",
        1.1,
        "float",
        null
       ],
   "show_all":
      ["Show everything",
        "Do you want to show every single item in the whole world",
        true,
        "bool",
        null
       ],
   "show_yesno":
      ["Really everything",
        "Do you really want to show every single item in the whole world",
        false,
        "yesno",
        null
       ],
   "something":
      ["A non empty field",
        "You really have to enter something",
        "a",
        "str",
        "nonempty"
       ],
   "path2":
       ["Another path",
        "A second path used by the next question to join 2 together",
        "pypirc",
        "path",
        null
       ],
   "join_path":
       ["Compound path",
        "Joining of path & path2",
        "{path}/{path2}",
        "path",
        null
       ]
   }
