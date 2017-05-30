# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

from pprint import pprint
from ama.terminal import TerminalAsker

__version__ = '0.1'

def test_Terminal():
    title = 'Test questions'
    preamble = 'Please enter values for the following settings'

    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.json')
    with open(filename) as question_stream:
        asker = TerminalAsker(title, preamble, ds=question_stream)
        new_answers = asker.ask(all_questions=True)
        pprint(new_answers)


if __name__ == '__main__':
    test_Terminal()
