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

"""Provides a dictionary of validation functions to test values. Values
are checked that they...

:str: can be converted to a string 
:bool: can be converted to a boolean value
:int: can be converted to an integer value
:float: can be converted to a floating point value
:yesno: match one of 'yes', 'y', 'no', 'n' with any case plus True and False
:re(regexp): matches the regular expression `regexp`
:path: is a valid path name that exists
:path(empty): is a valid path name that is empty
:path(nonempty): is a valid path name that is not empty
:path(pathspec): is a valid path name that contains files that conform to `filespec`

`pathspec` is of the form [+-]glob where the leading '+' indicates that
the path must include a file that matches the pattern and '-' indicates that
it must not include files that match pattern. Multiple pathspecs can be
specified separated by commas.
"""

import re
import csv
import glob
from io import StringIO
from os import path, listdir
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

def validate_path(value):
    is_dir = path.exists(value) and path.isdir(value)
    if not is_dir:
        raise ValueError('Please enter a valid path name.')
    return value

def validate_path_empty(value):
    is_dir = path.exists(value) and path.isdir(value)
    if not is_dir:
        raise ValueError(('Please enter a valid path name.'))
    
    if len(listdir(value)) != 0:
        raise ValueError(('Please enter a valid path name '
                               'for which the path is empty.'))
    return value

def validate_path_nonempty(value):
    is_dir = path.exists(value) and path.isdir(value)
    if not is_dir:
        raise ValueError(('Please enter a valid path name.'))
    
    if len(listdir(value)) == 0:
        raise ValueError(('Please enter a valid path name '
                          'for which the path is not empty.'))
    return value

def path_includes_file(path, filespec):
    fname = path.join(path, filespec)
    return path.exists(fname)

def path_does_not_include_file(path, filespec):
    fname = path.join(path, filespec)
    return not path.exists(fname)

def validate_path_with_spec(pathspec):
    reader = csv.reader(StringIO(unicode(pathspec)))
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
            if len(glob.glob(path.join(value, spec))) == 0:
                not_found.append(spec)
        
        found = []
        for spec in not_included:
            if len(glob.glob(path.join(value, spec))) != 0:
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
    if date_format == '':
        date_format = DEFAULT_DATE_FORMAT
    
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
            raise ValueError('Please enter a valid date in %s date_format.' % f)
        
    return validate

def validate_time(time_format=DEFAULT_TIME_FORMAT):
    if time_format == '':
        time_format = DEFAULT_TIME_FORMAT
        
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
            raise ValueError('Please enter a valid time in %s time_format.' % f)
        
    return validate


def extract_spec(key):
    start = key.find('(')
    if start != -1 and key[-1] == ')':
        return key[start+1:-1]
    else:
        return ''
    

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
    
        ep_match = self._entry_point_re.match(key)
        if ep_match is not None:
            func = load_entry_point(key)
            self._validators[key] = func
            return func
        
        return None

Validators = _Registry()

