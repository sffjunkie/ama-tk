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

import json
from string import Formatter
from collections import namedtuple, OrderedDict

_Question = namedtuple('question', 'key label type default help_text validator depends_on')
def Question(key, label, answer_type='str', default=None, help_text='', validator=None, depends_on=[]):
    return _Question(key, label, answer_type, default, help_text, validator, depends_on)


class Asker(object):
    def __init__(self, filename=''):
        if filename != '':
            with open(filename) as fp:
                data = fp.read()
                self._questions = json.loads(data, object_pairs_hook=OrderedDict)
        else:
            self._questions = None
    
    def ask(self, questions=None, initial_answers=None, all_questions=True, validators={}):
        """Ask the questions and return the answers
        
        :param questions: The questions to prompt for answers. Can either be
                          a json formatted string or a dict subclass
        :type questions:  string or dict
        :param initial_answers:   A dictionary containing the already answered
                          questions
        :type initial_answers:    dict
        :param all_questions: If True only the already unanswered questions
                              will be asked; if False all questions will be
                              asked.
        :type all_questions:  bool
        :param validators: A dictionary of custom validator functions
        :type validators: dict
        :returns: The answers
        :rtype: OrderedDict
        """
    
        if questions is None and self._questions is not None:
            questions = self._questions
            
        if not isinstance(questions, dict):
            questions = json.loads(questions, object_pairs_hook=OrderedDict)
    
        if initial_answers is None:
            initial_answers = {}
        
        for key, question in questions.items():
            if all_questions or key not in initial_answers:
                default = initial_answers.get(key, question[2])
                
                depends_on = self._find_dependencies(default)
                
                q = Question(key, question[0], question[1],
                             default, question[3], question[4],
                             depends_on)
                self.add_question(key, q)

        result = self.go(initial_answers)
        return result

    def go(self):
        raise NotImplemented
    
    def _find_dependencies(self, default):
        """Returns a list of fields the default uses""" 
        
        f = Formatter()
        dependencies = []
        for _text, field, _format_spec, _conversion in f.parse(default):
            if field is not None:
                dependencies.append(field)
        
        return dependencies
    