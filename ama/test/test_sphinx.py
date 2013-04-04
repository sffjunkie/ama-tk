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

import sys
import os.path
p = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, p)

from pprint import pprint
from ama.terminal import TerminalAsker

def test_Console():
    version = '1.1.3'
    title = 'Welcome to the Sphinx %s quickstart utility.' % version
    preamble = 'Please enter values for the following settings (just press Enter to\naccept a default value, if one is given in brackets).'
    answers = {u'batchfile': 'n'}
    asker = TerminalAsker(title, preamble, 'sphinx.json')    
    new_answers = asker.ask(initial_answers=answers, all_questions=True)
    pprint(new_answers)
    

if __name__ == '__main__':
    test_Console()
    