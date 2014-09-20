# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, p)

from pprint import pprint
from ama.terminal import TerminalAsker

def test_Console():
    version = '1.1.3'
    title = 'Welcome to the Sphinx %s quickstart utility.' % version
    preamble = 'Please enter values for the following settings (just press Enter to\naccept a default value, if one is given in brackets).'
    answers = {u'batchfile': 'n'}

    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sphinx.json')
    with open(filename) as qs:
        asker = TerminalAsker(title, preamble, ds=qs)
        new_answers = asker.ask(initial_answers=answers, all_questions=True)
        pprint(new_answers)


if __name__ == '__main__':
    test_Console()
