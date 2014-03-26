# Copyright 2009-2013, Simon Kennedy, code@sffjunkie.co.uk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Provides a dictionary of validation functions to test values.

========================  ======================================================
Validator Name            Tests that the value...
========================  ======================================================
``str``                   can be converted to a string 
``bool``                  can be converted to a boolean value
``int``                   can be converted to an integer value
``float``                 can be converted to a floating point value
``yesno``                 matches one of ``yes``, ``y``, ``no``, ``n`` with any
                          case plus True and False
:samp:`re({regexp})`      matches the regular expression `regexp`
``path``                  is a valid path name that exists
``path(empty)``           is a valid path name that is empty
``path(nonempty)``        is a valid path name that is not empty
:samp:`path({pathspec})`  is a valid path name that contains files that conform
                          to `pathspec`
                    
                          `pathspec` is of the form :samp:`[+-]{glob}` where the
                          leading ``+`` indicates that the path must include a
                          file that matches the glob and ``-`` indicates that it
                          must not include files that match the glob. Multiple
                          pathspecs can be specified separated by commas.
                  
:samp:`date({datespec})`  is a valid date that matches the *datespec* where
                          *datespec* follows the standard Python
                          :meth:`~datetime.datetime.strptime`
                          format string. 
:samp:`time({timespec})`  is a valid time that matches the *timespec* where
                          *timespec* follows the standard Python
                          :meth:`~datetime.datetime.strptime`
                          format string. 
:samp:`color({format})`   is a valid color in the specified format where the
                          format is one of ``hex`` where colors are specified
                          as per CSS Hex RGB or ``rgb`` where colors are
                          specified in the following format
                          :samp:`rgb({red},{green},{blue})`
                          Returns a 3 element iterable of the RGB Values 
========================  ======================================================
"""

import os
import re
import csv
import sys
import glob
import tempfile
from io import StringIO
from datetime import datetime, date, time

try:
    from pkg_resources import load_entry_point
except:
    load_entry_point = lambda x: None

__all__ = ['Validators']

DEFAULT_TIME_FORMAT = '%H:%M'
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

def validate_str(value):
    return str(value)

def validate_bool(value):
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
        raise ValueError('Please enter a valid boolean value')
    
def validate_int(value):
    if value == '':
        return 0
    
    try:
        return int(value)
    except:
        raise ValueError('Please enter an integer value')
    
def validate_float(value):
    if value == '':
        return 0.0
    
    try:
        return float(value)
    except:
        raise ValueError('Please enter a floating point value')

def validate_regex(regex):
    def validate(value):
        r = re.compile(regex)
        m = r.match(value)
        if m is not None:
            return value
        else:
            raise ValueError(('Please enter a string which matches'
                                   'the regular expression %s' % regex))
    
    return validate

def validate_could_be_path(value):
    temp_path = tempfile.gettempdir()
    
    if 'win' in sys.platform and value[1] ==':':
        value = value[2:]
        
    value = value.strip(os.sep)
    
    path_name = os.path.join(temp_path, value)
    
    try:
        os.makedirs(path_name)
        os.rmdir(path_name)
    except:
        raise ValueError('Please enter a valid path name')

def validate_path(value):
    is_dir = os.path.exists(value) and os.path.isdir(value)
    if not is_dir:
        raise ValueError('Please enter a valid path name.')
    return value

def validate_path_empty(value):
    is_dir = os.path.exists(value) and os.path.isdir(value)
    if not is_dir:
        raise ValueError(('Please enter a valid path name.'))
    
    if len(os.listdir(value)) != 0:
        raise ValueError(('Please enter a valid path name '
                               'for which the path is empty.'))
    return value

def validate_path_nonempty(value):
    is_dir = os.path.exists(value) and os.path.isdir(value)
    if not is_dir:
        raise ValueError(('Please enter a valid path name.'))
    
    if len(os.listdir(value)) == 0:
        raise ValueError(('Please enter a valid path name '
                          'for which the path is not empty.'))
    return value

def path_includes_file(path, filespec):
    fname = os.path.join(path, filespec)
    return os.path.exists(fname)

def path_does_not_include_file(path, filespec):
    fname = os.path.join(path, filespec)
    return not os.path.exists(fname)

def validate_path_with_spec(pathspec):
    reader = csv.reader(StringIO(pathspec))
    included = []
    not_included = []
    for row in reader:
        for elem in row:
            if elem.startswith('+'):
                included.append(elem[1:].strip('"'))
            elif elem.startswith('-'):
                not_included.append(elem[1:].strip('"'))

    def validate(value):
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
            msg_elem = ['Directory %s' % value]
            if not_found_count > 0:
                msg_elem.append('should contain files matching %s' % ','.join(included))
                
            if found_count > 0:
                if not_found_count > 0:
                    msg_elem.append('and')

                msg_elem.append('should not contain files matching %s' % ','.join(not_included))
                
            msg = ' '.join(msg_elem)
            raise ValueError(msg)
            
        return value
    
    return validate

def validate_nonempty(value):
    if value is None or str(value) == '':
        raise ValueError("Please enter something in this field.")
    return value

def validate_date(date_format=DEFAULT_DATE_FORMAT):
    def validate(value):
        if value is None or value == '':
            return ''
        
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, date):
            return value
        
        try:
            d = datetime.strptime(value, '%Y-%m-%d')
            return d.date()
        except:
            f = date_format
            format_conv = {'%Y': 'YYYY', '%y': 'YY', '%m': 'MM', '%d': 'DD'}
            for k, v in format_conv.items(): 
                f = f.replace(k, v)
            raise ValueError('Please enter a valid date in %s format.' % f)
        
    return validate

def validate_time(time_format=DEFAULT_TIME_FORMAT):
    def validate(value):
        if value is None or value == '':
            return ''
        
        if isinstance(value, time):
            return value

        try:
            d = datetime.strptime(value, time_format)
            return d.time()
        except:
            f = time_format
            format_conv = {'%H': 'hh', '%M': 'mm', '%S': 'ss'}
            for k, v in format_conv.items(): 
                f = f.replace(k, v)
            raise ValueError('Please enter a valid time in %s format.' % f)
        
    return validate

def extract_spec(key):
    start = key.find('(')
    if start != -1 and key[-1] == ')':
        return key[start+1:-1]
    else:
        return ''

def validate_color(colorspec):
    def validate_rgb(value):
        elems = value[4:-1].split(',')
        if len(elems) == 3:
            return tuple(map(int, elems))
        else:
            raise ValueError('Please enter a valid color in rgb(r,g,b) or #rrggbb format')
    
    def validate_hex(value):
        if value[0] == '#':
            if len(value) == 7:
                # The following to_iterable function is based on the
                # :func:`grouper` function in the Python standard library docs
                # http://docs.python.org/library/itertools.html
                def to_iterable():
                    args = [iter(value[1:])]*2
                    return tuple(map(lambda t: int('%s%s' % t, 16),
                        zip(*args)))
            elif len(value) == 4:
                def to_iterable():
                    return tuple(map(lambda t: int('%s%s' % (t, t), 16),
                        value[1:]))
                
            return to_iterable()
    
    if colorspec == 'rgb':
        return validate_rgb
    elif colorspec == 'hex':
        return validate_hex


class _Registry():
    def __init__(self):
        self._validators = {
            'str': lambda value: str(value),
            'yesno': validate_bool,
            'bool': validate_bool,
            'int': validate_int,
            'float': validate_float,
            # 're(regex)'
            'path': validate_path,
            'path(empty)': validate_path_empty,
            'path(nonempty)': validate_path_nonempty,
            # 'path(pathspec)'
            'nonempty': validate_nonempty,
            # 'date(datespec)': validate_date,
            # 'time(timespec)': validate_time,
            #'color(format)': validate_color,
        }
        
        self._entry_point_re = re.compile('\w+(\.\w)?\:\w+(\.\w)?')

    def __getitem__(self, key):
        if key is None:
            return None
        
        if key in self._validators:
            return self._validators[key]
        
        if key.startswith('re'):
            spec = extract_spec(key)
            if spec != '':
                regex = key[3:-1]
                func = validate_regex(regex)
            else:
                func = lambda value: str(value)
            self._validators[key] = func
            return func
        
        elif key.startswith('path'):
            spec = extract_spec(key)
            if spec != '':
                spec = key[5:-1]
                func = validate_path_with_spec(spec)
            else:
                func = validate_path
            self._validators[key] = func
            return func
        
        elif key.startswith('date'):
            spec = extract_spec(key)
            if spec != '':
                spec = key[5:-1]
                func = validate_date(spec)
            else:
                func = validate_date()
            self._validators[key] = func
            return func
        
        elif key.startswith('time'):
            spec = extract_spec(key)
            if spec != '':
                spec = key[5:-1]
                func = validate_time(spec)
            else:
                func = validate_time()
            self._validators[key] = func
            return func
        
        elif key.startswith('color'):
            spec = extract_spec(key)
            func = validate_color(spec)
            self._validators[key] = func
            return func
            
        ep_match = self._entry_point_re.match(key)
        if ep_match is not None:
            func = load_entry_point(key)
            self._validators[key] = func
            return func
        
        return None

Validators = _Registry()
