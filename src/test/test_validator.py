# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import tempfile
import datetime
import gettext
from ama.validator import get_validator, str_to_kwargs, str_to_elems

from pytest import raises

install_args = {}
if sys.version_info < (3, 0):
    install_args['unicode'] = True

gettext.install('ama', **install_args)


def test_str_to_kwargs():
    assert str_to_kwargs('a=1') == {'a': '1'}

    result = str_to_kwargs('a=1|b=2')
    assert 'b' in result
    assert result['b'] == '2'

    result = str_to_kwargs('a=1|b=2', allowed=None)
    assert 'a' in result
    assert 'b' in result

    result = str_to_kwargs('a=1|b=2', allowed=['b'])
    assert 'a' not in result

    result = str_to_kwargs('a=,')
    assert result['a'] == ','


def test_str_to_elems():
    assert 'a' in str_to_elems('a')
    assert 'a' in str_to_elems('a|b')
    assert 'b' in str_to_elems('a|b')
    assert 'b c' in str_to_elems('a|"b c"')
    assert 'a' in str_to_elems('a\nb')
    assert 'b' in str_to_elems('a\nb')


def test_validate_nonempty():
    v = get_validator('nonempty')
    with raises(ValueError):
        v('')


def test_validate_constant():
    v = get_validator('constant', 'else')
    assert v('something') == 'else'


def test_validate_str():
    v = get_validator('str')
    assert v('44') == '44'
    assert v(55) == '55'


def test_validate_str_empty():
    v = get_validator('str')
    assert v('') == ''


def test_validate_str_nonempty():
    v = get_validator('str', 'nonempty')
    with raises(ValueError):
        v('')


def test_validate_str_minlength():
    v = get_validator('str', 'min=3')
    assert v('abcd') == 'abcd'

    with raises(ValueError):
        v('ab')


def test_validate_str_maxlength():
    v = get_validator('str', 'max=3')
    assert v('abc') == 'abc'

    with raises(ValueError):
        v('abcd')


def test_validate_yesno():
    v = get_validator('yesno')
    assert v('yes') == True
    assert v('YES') == True
    assert v('y') == True
    assert v('Y') == True

    assert v('no') == False
    assert v('NO') == False
    assert v('n') == False
    assert v('N') == False


def test_validate_yesno_fail():
    v = get_validator('yesno')

    with raises(ValueError):
        v('wally')


def test_validate_bool():
    v = get_validator('bool')
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


def test_validate_bool_fail():
    v = get_validator('bool')
    with raises(ValueError):
        v('wally')


def test_validate_int():
    v = get_validator('int')
    assert v(1) == 1
    assert v(12) == 12


def test_validate_int_string():
    v = get_validator('int')
    assert v('12') == 12


def test_validate_int_fail():
    v = get_validator('int')
    with raises(TypeError):
        v(1.0)

    with raises(ValueError):
        v('1.0')

    with raises(ValueError):
        v('wally')


def test_validate_int_min():
    v = get_validator('int', 'min=3')
    assert v(3) == 3

    with raises(ValueError):
        v(2)


def test_validate_int_max():
    v = get_validator('int', 'max=3')
    assert v(3) == 3

    with raises(ValueError):
        v(4)


def test_validate_int_decimalfail():
    v = get_validator('int', 'decimal=i')

    with raises(ValueError):
        v('3i1')


def test_validate_float():
    v = get_validator('float')
    assert v(1.2) == 1.2


def test_validate_float_string():
    v = get_validator('float')
    assert v('1.2') == 1.2


def test_validate_float_fail():
    v = get_validator('float')
    with raises(TypeError):
        v(1)

    with raises(ValueError):
        v('1')

    with raises(ValueError):
        v('wally')


def test_validate_float_decimal():
    v = get_validator('float', 'decimal=,')
    assert v('1,2') == 1.2


def test_validate_float_min():
    v = get_validator('float', 'min=3.1')
    assert v(3.1) == 3.1

    with raises(TypeError):
        v(3)


def test_validate_float_max():
    v = get_validator('float', 'max=3.1')
    assert v(3.1) == 3.1

    with raises(ValueError):
        v(3.2)


def test_validate_float_minmax():
    v = get_validator('float', 'min=3.1|max=4')
    assert v(3.1) == 3.1

    with raises(TypeError):
        v(3)


def test_validate_float_minmaxdecimal():
    v = get_validator('float', 'min=3.1|max=4|decimal=i')
    assert v('3i1') == 3.1

    with raises(TypeError):
        v(3)

    with raises(ValueError):
        v('4i15')


def test_validate_number():
    v = get_validator('number')
    assert v(1) == 1
    assert v(12) == 12
    assert v(1.2) == 1.2


def test_validate_regex():
    v = get_validator('re', r'\d+')
    assert v('12') == '12'


def test_validate_regex_fail():
    with raises(ValueError):
        v = get_validator('re', '\\d+')
        assert v('a') == '12'


def test_validate_path():
    v = get_validator('path')
    assert v('C:\\windows') == 'C:\\windows'


def test_validate_path_empty():
    v = get_validator('path', 'empty')
    d = tempfile.mkdtemp()
    assert v(d) == d
    os.rmdir(d)


def test_validate_path_empty_fail():
    v = get_validator('path', 'empty')
    d = tempfile.mkdtemp()
    with tempfile.NamedTemporaryFile(dir=d) as _f:
        with raises(ValueError):
            v(d)
    os.rmdir(d)


def test_validate_path_nonempty():
    v = get_validator('path', 'nonempty')
    assert v('C:\\windows') == 'C:\\windows'


def test_validate_path_nonempty_fail():
    v = get_validator('path', 'nonempty')
    d = tempfile.mkdtemp()
    with raises(ValueError):
        v(d)
    os.rmdir(d)


def test_validate_path_contains():
    with tempfile.TemporaryFile() as f:
        dname, fname = os.path.split(f.name)
        v = get_validator('path', '+%s' % fname)
        assert v(dname) == dname


def test_validate_path_contains_fail():
    v = get_validator('path', '+file.tmp')
    d = tempfile.mkdtemp()
    with raises(ValueError):
        v(d)
    os.rmdir(d)


def test_validate_path_does_not_contain():
    v = get_validator('path', '-file.tmp')
    d = tempfile.mkdtemp()
    assert v(d) == d
    os.rmdir(d)


def test_validate_path_does_not_contain_fail():
    with tempfile.TemporaryFile() as f:
        dname, fname = os.path.split(f.name)
        v = get_validator('path', '-%s' % fname)
        with raises(ValueError):
            assert v(dname)


def test_validate_path_contains_and_does_not_contain():
    with tempfile.TemporaryFile() as f:
        dname, fname = os.path.split(f.name)
        v = get_validator('path', '+%s|-file.tmp' % fname)
        assert v(dname) == dname


def test_validate_path_contains_and_does_not_contain_fail():
    d = tempfile.mkdtemp()
    with tempfile.TemporaryFile(dir=d) as f:
        dname, fname = os.path.split(f.name)
        v = get_validator('path', '+*.tmp|-%s' % fname)
        with raises(ValueError):
            v(dname)
    os.rmdir(d)


def test_validate__date():
    v = get_validator('date')
    d = datetime.date(2013, 4, 23)
    assert v('2013-04-23') == d


def test_validate_color():
    v1 = get_validator('color', 'rgbhex')
    assert v1('#abc') == '#abc'
    assert v1('#aabbcc') == '#aabbcc'

    v2 = get_validator('color', 'rgb')
    assert v2('rgb(170, 187, 204)') == (170, 187, 204)


def test_validate__email():
    v = get_validator('email')
    assert v('joeb@example.com') == 'joeb@example.com'
