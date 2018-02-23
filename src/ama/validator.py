# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com
# pylint: disable=unused-argument

"""Provides access to a registry of validation functions.

Functions are returned via the :func:`get_validator` function and can be refined
by passing a specification which alters what passes the validation.

All validators throw :class:`TypeError` if the value's type cannot be validated
and :class:`ValueError` if the value fails validation.

========================  ======================================================
Validator Name            Tests that the value...
========================  ======================================================
``nonempty``              is not None or an empty string
``constant``              always returns the same value
``str``                   can be converted to a string
``int``                   can be converted to an integer value
``float``                 can be converted to a floating point value
``bool``                  can be converted to a boolean value
``yesno``                 matches one of ``yes``, ``y``, ``no``, ``n`` with any
                          case plus 1, 0, True and False
``re``                    matches the regular expression.
``path``                  is a valid path
``date``                  is a valid date
``time``                  is a valid time
``color``                 is a valid RGB or RGB hex color
``email``                 is a valid email address
========================  ======================================================
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import csv
import gettext
import glob
import shutil
import string
import tempfile
from io import StringIO
from datetime import datetime, date, time
from functools import partial

try:
    from pkg_resources import load_entry_point
except:
    load_entry_point = lambda x: None

import re
try:
    import pyisemail
    PYISEMAIL = True
except ImportError:
    PYISEMAIL = False


if sys.version_info < (3, 0):
    gettext.install('ama', unicode=True) #pylint: disable=unexpected-keyword-arg
else:
    gettext.install('ama')


DEFAULT_TIME_FORMAT = '%H:%M'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'


if sys.version_info >= (3, 0):
    str_type = str
    csv.register_dialect('ama', delimiter='|')
else:
    str_type = basestring
    csv.register_dialect('ama', delimiter=b'|')


def str_to_elems(string):
    if sys.version_info < (3, 0) and isinstance(string, basestring):
        string = string.decode('UTF-8')

    ds = StringIO(string)
    reader = csv.reader(ds, dialect=csv.get_dialect('ama'))
    for row in reader:
        for elem in row:
            yield elem


def str_to_kwargs(string, allowed=None):
    kwargs = {}
    for elem in str_to_elems(string):
        option, value = elem.split('=')
        if not allowed or option in allowed:
            kwargs[option] = value

    return kwargs


def NonEmpty(*args, **kwargs):
    """Create a validator that checks that any value is provided"""

    msg = kwargs.get('message', _('Please enter anything.'))

    def validate(value):
        if not value:
            raise ValueError(msg)
        return value

    return validate


def Constant(*args, **kwargs):
    """Create a validator that always return the same value."""

    def validate(value):
        return args[0]

    return validate


def OneOf(*args, **kwargs):
    """Create a validator that checks that the value is one of the those provided."""

    def validate(value):
        msg = _('Value must be one of %s')

        if value in args:
            return value
        else:
            raise ValueError(msg % ', '.join(args))

    return validate


def Str(*args, **kwargs):
    """Create a validator that checks that the value is a valid string
    according to the `spec`

    :param spec: The specification to check the string against.
                 Can be either

                 None
                      Anything that can be converted to a string passes

                 The string ``nonempty``
                     a string of length greater than 1 passes

                 A string of `argument=value` pairs separated by commas.
                     Checks the string matches based on the arguments specified

                     The following arguments can be specified.

                         | ``min`` - The minimum number of characters
                         | ``max`` - The maximum number of characters

                     e.g. "min=3,max=6" means the string must be between 3 and 6
                     characters long.
    :type spec:  str
    """

    def validate(value, **kwargs):
        if value is None or value=='':
            return ''
        
        try:
            value = str(value)
        except:
            raise ValueError(_('Unable to convert value to string'))

        length = len(value)

        if 'min' in kwargs:
            min_ = int(kwargs['min'])
            if length < min_:
                raise ValueError(_('String must be at least %d characters') % min_)

        if 'max' in kwargs:
            max_ = int(kwargs['max'])
            if length > max_:
                raise ValueError(_('String must be a maximum of %d characters') % max_)

        return value

    if args and args[0] == 'nonempty':
        return NonEmpty()
    else:
        return partial(validate, **kwargs)


def Int(*args, **kwargs):
    """Create a validator that checks that the value is a valid integer
    according to the `spec`

    :param spec: The specification to check the integer against.
                 Can be either

                 None
                      Anything that is an integer passes. e.g. 1 and "1" are
                      valid integers but 1.2, "1.2" or "chas" are not.

                 A string of `argument=value` pairs separated by commas.
                     Alters how the integer is validated. The following arguments
                     can be specified.

                         | ``min`` - The minimum value
                         | ``max`` - The maximum value

                     e.g. "min=3,max=6" means the value must be between 3 and 6.
    :type spec:  str
    """

    def validate(value, **kwargs):
        msg = _('Invalid integer value')

        if isinstance(value, float):
            raise TypeError(msg)

        if isinstance(value, str_type):
            decimal = kwargs.get('decimal', '.')

            if decimal in value:
                raise ValueError(msg)

        try:
            value = int(value)
        except:
            raise ValueError(msg)

        if 'min' in kwargs:
            min_ = int(kwargs['min'])
            if value < min_:
                raise ValueError('Integer value less than minimum %d' % min_)

        if 'max' in kwargs:
            max_ = int(kwargs['max'])
            if value > max_:
                raise ValueError('Integer value greater than maximum %d' % max_)

        return value

    return partial(validate, **kwargs)


def Float(*args, **kwargs):
    """Create a validator that checks that the value is a valid float
    according to the `spec`

    :param spec: The specification to check the float against.
                 Can be either

                 None
                      Anything that is a float passes. e.g. 1.2 and "1.2" are
                      valid floats but 1, "1" or "dave" are not.

                 A string of `argument=value` pairs separated by commas.
                     Alters how the float is validated. The following arguments
                     can be specified.

                         | ``min`` - The minimum value
                         | ``max`` - The maximum value
                         | ``decimal`` - The character to consider as the decimal separator
                         | ``nocoerce`` - Disable coercing int to float

                     e.g. "min=3.1,max=6.0" means the value must be between
                     3.1 and 6.0; "decimal=\\\\," means that "33,234" is a valid float.
    :type spec:  str
    """

    def validate(value, **kwargs):
        msg = _('Invalid floating point value')

        if 'nocoerce' in kwargs and isinstance(value, int):
            raise TypeError(msg)

        if isinstance(value, str_type):
            decimal = kwargs.get('decimal', '.')

            if 'nocoerce' in kwargs and decimal not in value:
                raise ValueError(msg)
            elif decimal != '.':
                value = value.replace(decimal, '.')

        try:
            value = float(value)
        except:
            raise ValueError(msg)

        if 'min' in kwargs:
            min_ = float(kwargs['min'])
            if value < min_:
                raise ValueError('Float value less than minimum %f' % min_)

        if 'max' in kwargs:
            max_ = float(kwargs['max'])
            if value > max_:
                raise ValueError('Float value greater than maximum %f' % max_)

        return value

    return partial(validate, **kwargs)


def Number(*args, **kwargs):
    """Create a validator that checks that the value is a valid number
    according to the `spec`

    :param spec: The specification to check the integer against.
                 Can be either

                 None
                      Anything that is a number passes.

                 A string of `argument=value` pairs separated by commas.
                     Check s the integer matches based on the arguments specified

                     The following arguments can be specified.

                         | ``min`` - The minimum value
                         | ``max`` - The maximum value
                         | ``decimal`` - The character to consider as the decimal separator

                     e.g. "min=3,max=6" means the value must be between 3 and 6.
    :type spec:  str
    """

    def validate(value, **kwargs):
        msg = _('Invalid number')

        if isinstance(value, str_type):
            decimal = kwargs.get('decimal', '.')
            if decimal != '.':
                value = value.replace(decimal, '.')

        try:
            value = float(value)
        except ValueError:
            raise ValueError(msg)

        if 'min' in kwargs:
            min_ = float(kwargs['min'])
            if value < min_:
                raise ValueError('Float value less than minimum %d' % min_)

        if 'max' in kwargs:
            max_ = float(kwargs['max'])
            if value > max_:
                raise ValueError('Float value greater than maximum %d' % max_)

        return value

    return partial(validate, **kwargs)


def Bool(*args, **kwargs):
    """Create a validator that checks that the value is a valid bool."""

    def validate(value):
        msg = _('Invalid boolean value')
        true_values = ['true', '1', 'yes', 'y']
        false_values = ['false', '0', 'no', 'n']

        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return bool(value)
        elif str(value).lower() in true_values:
            return True
        elif str(value).lower() in false_values:
            return False
        else:
            raise ValueError(msg)

    return validate


def Regex(*args, **kwargs):
    """Create a validator that checks that the value matches a regular
    expression.
    """
    # if no regex provided just check that the value can be converted to a string
    if len(args) == 0:
        return lambda value: str(value)

    def validate(value, **kwargs):
        msg = _('Please enter a string which matches the regex')

        regex = kwargs.pop('regex', None)
        if regex:
            m = re.match(regex, value)
            if m is not None:
                return value
            else:
                raise ValueError('%s %s' % (msg, regex))
        else:
            return value

    kwargs['regex'] = args[0]
    return partial(validate, **kwargs)


def Path(*args, **kwargs):
    """Create a validator that checks that the value is a valid path.

    The meaning of valid is determined by the `spec` argument

    :param spec: Determines what is a valid path.

        ``existing``
            is a path that exists (the default)

        ``empty``
            is a path that is empty

        ``nonempty``
            is a path that is not empty

        ``new``
            is a path that does not exist and is a valid name for a path

        :samp:`{pathspec}`
            is a valid path name that contains files that conform to `pathspec`

            `pathspec` is of the form :samp:`[+-]{glob}` where the
            leading ``+`` indicates that the path must include a
            file that matches the glob and ``-`` indicates that it
            must not include files that match the glob. Multiple
            pathspecs can be specified separated by commas.
    :type spec:  str
    """

    def validate_path_existing(value):
        """Validate that path exists"""

        msg1 = _('Path does not exist.')

        is_dir = os.path.exists(value) and os.path.isdir(value)
        if not is_dir:
            raise ValueError(msg1)
        return value

    def validate_path_new(value):
        """Validate that the path could be created."""

        msg1 = _('Path already exists.')
        msg2 = _('Invalid path name.')

        if value == '':
            return ''

        if os.path.isdir(value):
            raise ValueError(msg1)

        if os.path.isabs(value):
            dummy, p = os.path.splitdrive(value)
        else:
            p = value

        if p[0] == '\\' or p[0] == '/':
            p = p[1:]

        try:
            tf = tempfile.mkdtemp(prefix=p)
            shutil.rmtree(tf)
            return value
        except OSError:
            raise ValueError(msg2)

    def validate_path_empty(value):
        msg1 = _('Path does not exist.')
        msg2 = _('Path should be empty.')

        is_dir = os.path.exists(value) and os.path.isdir(value)
        if not is_dir:
            raise ValueError(msg1)

        if len(os.listdir(value)) != 0:
            raise ValueError(msg2)
        return value

    def validate_path_nonempty(value):
        msg1 = _('Path does not exist.')
        msg2 = _('Path should contain files.')

        is_dir = os.path.exists(value) and os.path.isdir(value)
        if not is_dir:
            raise ValueError(msg1)

        if len(os.listdir(value)) == 0:
            raise ValueError(msg2)
        return value

    def validate_path_with_spec(*args):
        included = []
        not_included = []
        for elem in str_to_elems(args[0]):
            if elem.startswith('+'):
                included.append(elem[1:].strip('"'))
            elif elem.startswith('-'):
                not_included.append(elem[1:].strip('"'))

        def validate(value):
            msg_start = _('Path %s')
            msg_should_contain = _('should contain files matching %s')
            msg_should_not_contain = _('should not contain files matching %s')

            not_found = []
            for spec in included:
                if len(glob.glob(os.path.join(value, spec))) == 0:
                    not_found.append(spec)

            found = []
            for spec in not_included:
                if len(glob.glob(os.path.join(value, spec))) != 0:
                    found.append(spec)

            found_count = len(found)
            not_found_count = len(not_found)
            if found_count != 0 or not_found_count != 0:
                msg_elem = [msg_start % value]
                if not_found_count > 0:
                    msg_elem.append(msg_should_contain % ','.join(included))

                if found_count > 0:
                    if not_found_count > 0:
                        msg_elem.append(_('and'))

                    msg_elem.append(msg_should_not_contain % ','.join(not_included))

                msg = ' '.join(msg_elem)
                raise ValueError(msg)

            return value

        return validate

    if not args or args[0] == 'existing':
        return validate_path_existing
    elif args[0] == 'new':
        return validate_path_new
    elif args[0] == 'empty':
        return validate_path_empty
    elif args[0] == 'nonempty':
        return validate_path_nonempty
    else:
        return validate_path_with_spec(*args)


def Date(*args, **kwargs):
    """Create a validator that checks that the value is a valid date.

    :param spec: The date format to accept if a string value is used.

                    ``spec`` follows the standard Python
                    :ref:`strftime <python:strftime-strptime-behavior>`
                    format string.
    :type spec:  str
    """
    if not args:
        spec = DEFAULT_DATE_FORMAT
    else:
        spec = args[0]

    def validate(value):
        msg = _('Invalid date for format %s')

        if value is None or value == '':
            return ''

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        try:
            d = datetime.strptime(value, spec)
            return d.date()
        except:
            f = spec
            format_conv = {'%Y': 'YYYY', '%y': 'YY', '%m': 'MM', '%d': 'DD'}
            for k, v in format_conv.items():
                f = f.replace(k, v)
            raise ValueError(msg % spec)

    return validate


def Time(*args, **kwargs):
    """Create a validator that checks that the value is a valid time.

    :param spec: The time format to accept if a string value is used.

                    ``spec`` follows the standard Python
                    :ref:`strftime <python:strftime-strptime-behavior>`
                    format string.
    :type spec:  str
    """
    if not args:
        spec = DEFAULT_TIME_FORMAT
    else:
        spec = args[0]

    def validate(value):
        msg = _('Invalid time for format %s')

        if value is None or value == '':
            return ''

        if isinstance(value, time):
            return value

        try:
            d = datetime.strptime(value, spec)
            return d.time()
        except:
            f = spec
            format_conv = {'%H': 'hh', '%M': 'mm', '%S': 'ss'}
            for k, v in format_conv.items():
                f = f.replace(k, v)
            raise ValueError(msg % spec)

    return validate


def Color(*args, **kwargs):
    """Create a validator that checks that the value is a valid color

    The color format, which is determined by the `spec` argument, can be one
    of the following

    * An RGB hex representation i.e. `#` followed by either 3 or 6 hex digits.
    * A string of the form 'rgb(R, G, B)' where R, G and B are floating point
      values between 0.0 and 1.0

    :param spec: The color type to accept either 'rgbhex' or 'rgb'
    :type spec:  str
    """
    def validate_rgb(value):
        if isinstance(value, (tuple, list)):
            return tuple(value[:3])
        elif value.startswith('rgb('):
            elems = value[4:-1].split(',')[:3]
        else:
            elems = value.split(',')[:3]

        return tuple(map(int, elems))

    def validate_hex(value):
        msg = _('Invalid RGB hex value')

        if value[0] == '#' and len(value) in (4, 7):
            if all([x in string.hexdigits for x in value[1:]]):
                return value

        raise ValueError(msg)

    if not args or args[0] == 'rgbhex':
        return validate_hex
    elif args[0] == 'rgb':
        return validate_rgb


def Email(*args, **kwargs):
    """Create a validator that checks that the value is a valid email address.

    If the :mod:`pyisemail` module is available then that is used to validate
    the email address otherwise a regular expression is used (which may produce
    false positives.)
    """
    def validate(value):
        msg = _('Invalid email address')

        if PYISEMAIL and 're' not in args:
            kwargs = str_to_kwargs(args[0])
            match = pyisemail.is_email(value, **kwargs)
        else:
            match = re.match(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$',
                         value,
                         flags=re.IGNORECASE)

        if not match:
            raise ValueError(msg)
        else:
            return value

    return validate


entry_point_re = re.compile(r'\w+(\.\w)?\:\w+(\.\w)?')

validators = {
    'nonempty': NonEmpty,
    'constant': Constant,
    'str': Str,
    'bool': Bool,
    'yesno': Bool,
    'int': Int,
    'float': Float,
    'number': Number,
    'path': Path,
    'date': Date,
    'time': Time,
    'color': Color,
    're': Regex,
    'password': Str,
    'email': Email,
}


def spec_to_args(spec):
    args = []
    kwargs = {}
    if spec:
        for elem in str_to_elems(spec):
            pos = elem.find('=')
            if pos == -1:
                args.append(elem)
            else:
                while True:
                    if elem[pos - 1] != '\\':
                        break

                    pos = elem.find('=', pos + 1)

                    if pos == -1:
                        break

                if pos != -1:
                    key = elem[:pos]
                    value = elem[pos + 1:]
                    kwargs[key] = value
                else:
                    args.append(elem)
    return args, kwargs


def get_validator(validator, spec=None):
    """Get a validation function

    :param validator: The name of the validator to create
    :type validator:  str
    :param spec: A specification to modify how the validator works
    :type spec:  str
    """
    
    if not entry_point_re.match(validator):
        func = validators[validator]

        args, kwargs = spec_to_args(spec)

        return func(*args, **kwargs)
    else:
        if validator in validators:
            return validators[validator]
        else:
            func = load_entry_point(validator)
            validators[validator] = func
            return func
