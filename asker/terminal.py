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

try:
    import readline
except ImportError:
    pass

try:
    input = raw_input
except:
    pass

from collections import OrderedDict

from asker import Asker
from asker.validator import Validators, validate_bool
from asker.ansi import bright_green, cyan, red

class TerminalAsker(Asker):
    def __init__(self, title, preamble='', filename=''):
        Asker.__init__(self, filename)
        self._title = title
        self._preamble = preamble
        self._ask = OrderedDict()
    
    def add_question(self, key, question):
        self._ask[key] = question
    
    def go(self, initial_answers):
        print(bright_green(self._title))
        print(bright_green('-'*len(self._title)))
        if self._preamble != '':
            print('\n%s' % self._preamble)
        print('\n')
           
        result = {}
        try:
            answers = {}
            for key, question in self._ask.items():
                answer = self.ask_question(question, initial_answers, answers)
                answers[key] = answer
                
            result[u'answers'] = answers
            result[u'result'] = 'ok'
        except (KeyboardInterrupt, EOFError):
            try:
                result[u'result'] = 'cancel'
                print('\n[Interrupted]\n')
            except:
                pass
            
        return result

    def ask_question(self, question, initial_answers, answers):
        prompt_tail = ''
        if question.type == 'yesno':
            prompt_tail = ' (y/n)'
            if question.default == True or question.default == 'y':
                prompt_tail += ' [y]'
            elif question.default == False or question.default == 'n':
                prompt_tail += ' [n]'
            default = validate_bool(question.default)
        else:
            try:
                default = question.default.format(**answers)
            except:
                default = question.default
            
            prompt_tail = ' [%s]' % default
        
        prompt = '%s%s: ' % (question.label, prompt_tail)
            
        while True:
            answer = input(cyan(prompt))
            stripped = answer.strip()
            if stripped == '?':
                print(question.help_text)
                continue
            
            if stripped == '':
                answer = default
                
            try:
                answer = self.validate(answer, question.type, question.validator)
            except Exception as err:
                print(red('* ' + str(err)))
                print(question.help_text)
                continue
            break
    
        return answer
                
    def validate(self, value, type_, validator):
        type_validator = Validators[type_]
        
        custom_validator = None
        if validator is not None:
            custom_validator = Validators[validator]
        
        if type_validator is None and custom_validator is not None:
            return value
        else:
            v1 = type_validator(value)
            if custom_validator is not None:
                return custom_validator(v1)
            else:
                return v1
