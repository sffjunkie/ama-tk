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
from collections import namedtuple, OrderedDict

_Question = namedtuple('question', 'key label type default help_text validator needs_format')
def Question(key, label, answer_type='str', default=None, help_text='', validator=None, needs_format=False):
    return _Question(key, label, answer_type, default, help_text, validator, needs_format)


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
                
                # When a question
                needs_format = False
                try:
                    formatted_default = default.format(**initial_answers)
                    if formatted_default != default:
                        needs_format = True
                except:
                    pass
                
                q = Question(key, question[0], question[1],
                             default, question[3], needs_format)
                self.add_question(key, q)

        result = self.go(initial_answers)
        return result

    def go(self):
        raise NotImplemented
    
