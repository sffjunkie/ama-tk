# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, p)

from pprint import pprint
from ama.terminal import TerminalAsker

__version__ = '0.1'

def test_Terminal():
    title = 'Test questions'
    preamble = 'Please enter values for the following settings'

    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sphinx.json')
    with open(filename) as qs:
        asker = TerminalAsker(title, preamble, ds=qs)    
        new_answers = asker.ask(all_questions=True)
        pprint(new_answers)
    

if __name__ == '__main__':
    test_Terminal()
    
