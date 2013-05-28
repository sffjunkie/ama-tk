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

import os
import tempfile
import datetime
from ama.validator import Validators, extract_spec

from pytest import raises

def test_validate_str():
    v = Validators['str']
    assert v('44') == '44'
    assert v(55) == '55'
    
def test_validate_yesno():
    v = Validators['yesno']
    assert v('yes') == True
    assert v('YES') == True
    assert v('y') == True
    assert v('Y') == True

    assert v('no') == False
    assert v('NO') == False
    assert v('n') == False
    assert v('N') == False
    
def test_validate_bool():
    v = Validators['bool']
    assert v(True) == True
    assert v(1) == True
    assert v('1') == True
    assert v('yes') == True
    assert v('YES') == True
    assert v('y') == True
    assert v('Y') == True

    assert v(False) == False
    assert v(0) == False
    assert v('0') == False
    assert v('no') == False
    assert v('NO') == False
    assert v('n') == False
    assert v('N') == False

def test_validate_int():
    v = Validators['int']
    assert v(1) == 1
    assert v(12) == 12

def test_validate_float():
    v = Validators['float']
    assert v(1) == 1.0
    assert v(1.2) == 1.2

def test_validate_regex():
    v = Validators['re(\\d+)']
    assert v('12') == '12'

def test_validate_path():
    v = Validators['path']
    assert v('C:\\windows') == 'C:\\windows'

def test_validate_path_empty():
    v = Validators['path(empty)']
    d = tempfile.mkdtemp()
    assert v(d) == d
    os.rmdir(d)

def test_validate_path_empty_fail():
    v = Validators['path(empty)']
    d = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(dir=d) as _f:
        with raises(ValueError):
            v(d)
    os.rmdir(d)

def test_validate_path_nonempty():
    v = Validators['path(nonempty)']
    assert v('C:\\windows') == 'C:\\windows'

def test_validate_path_nonempty_fail():
    v = Validators['path(nonempty)']
    d = tempfile.mkdtemp()
    with raises(ValueError):
        v(d)
    os.rmdir(d)

def test_validate_path_contains():
    with tempfile.TemporaryFile() as f:
        dname, fname = os.path.split(f.name)
        v = Validators['path(+%s)' % fname]
        assert v(dname) == dname

def test_validate_path_contains_fail():
    v = Validators['path(+file.tmp)']
    d = tempfile.mkdtemp()
    with raises(ValueError):
        v(d)
    os.rmdir(d)

def test_validate_path_does_not_contain():
    v = Validators['path(-file.tmp)']
    d = tempfile.mkdtemp()
    assert v(d) == d
    os.rmdir(d)

def test_validate_path_does_not_contain_fail():
    with tempfile.TemporaryFile() as f:
        dname, fname = os.path.split(f.name)
        v = Validators['path(-%s)' % fname]
        with raises(ValueError):
            assert v(dname)

def test_validate_path_contains_and_does_not_contain():
    with tempfile.TemporaryFile() as f:
        dname, fname = os.path.split(f.name)
        v = Validators['path(+%s,-file.tmp)' % fname]
        assert v(dname) == dname

def test_validate_path_contains_and_does_not_contain_fail():
    d = tempfile.mkdtemp()
    with tempfile.TemporaryFile(dir=d) as f:
        dname, fname = os.path.split(f.name)
        v = Validators['path(+*.tmp,-%s)' % fname]
        with raises(ValueError):
            v(dname)
    os.rmdir(d)

def test_date():
    v = Validators['date']
    d = datetime.date(2013, 04, 23)
    assert v('2013-04-23') == d
    
def test_extract_spec():
    assert extract_spec('re()') == ''
    assert extract_spec('re([0-9]?)') == '[0-9]?'
    
def test_validate_color():
    v1 = Validators['color(hex)']
    assert v1('#abc') == (170, 187, 204)
    assert v1('#aabbcc') == (170, 187, 204)
    
    v2 = Validators['color(rgb)']
    assert v2('rgb(170, 187, 204)') == (170, 187, 204)
    

if __name__ == '__main__':
    test_validate_str()
    test_validate_yesno()
    test_validate_bool()
    test_validate_int()
    test_validate_float()
    test_validate_regex()
    test_validate_path()
    test_validate_path_empty()
    test_validate_path_empty_fail()
    test_validate_path_nonempty()
    test_validate_path_nonempty_fail()
    test_validate_path_contains()
    test_validate_path_contains_fail()
    test_validate_path_does_not_contain()
    test_validate_path_does_not_contain_fail()
    test_validate_path_contains_and_does_not_contain()
    test_validate_path_contains_and_does_not_contain_fail()
    test_date()
    test_extract_spec()
    test_validate_color()
    