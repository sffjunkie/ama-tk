# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

from pprint import pprint
from ama.wx import WxAsker

__version__ = '0.1'

def test_Wx():
    title = 'Test questions'
    preamble = 'Please enter values for the following settings'

    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.json')
    with open(filename) as qs:
        asker = WxAsker(title, preamble, ds=qs, allow_invalid=False)
        new_answers = asker.ask(all_questions=True)
        pprint(new_answers)


if __name__ == '__main__':
    test_Wx()

