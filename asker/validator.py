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

from os import path

try:
    from pkg_resources import load_entry_point
except:
    load_entry_point = lambda x: None

class ValidationError(Exception):
    pass

def validate_yesno(value):
    if str(value).lower() in ['yes', 'y']:
        return True
    elif str(value).lower() in ['no', 'n']:
        return False
    elif value == True:
        return True
    elif value == False:
        return False
    else:
        raise ValidationError('Please enter one of "y", "Y", "n" or "N"')

def validate_bool(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, int):
        return bool(value)
    elif str(value).lower() in ['true', '1', 'yes', 'y']:
        return True
    elif str(value).lower() in ['false', '0', 'no', 'n']:
        return False
    else:
        raise ValidationError
    
def validate_int(value):
    if value == '':
        return 0
    
    try:
        return int(value)
    except:
        raise ValidationError('Please enter an integer value')

def validate_path(value):
    if path.exists(value) and not path.isdir(value):
        raise ValidationError("Please enter a valid path name.")
    return value

def validate_nonempty(value):
    if value is None or str(value) == '':
        raise ValidationError("Please enter some text.")
    return value
    

class ValidatorRegistry():
    def __init__(self):
        self._validators = {
            'str': lambda value: str(value),
            'int': validate_int,
            'bool': validate_bool,
            'path': validate_path,
            'nonempty': validate_nonempty,
            'yesno': validate_yesno,
        }

    def __getitem__(self, key):
        if key is None:
            return None
        
        if key in self._validators:
            return self._validators[key]
        elif key.find(':') != -1:
            func = load_entry_point(key)
            self._validators[key] = func
            return func
        else:
            return None

Validators = ValidatorRegistry()
