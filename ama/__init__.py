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

from ama.validator import Validators

import sys
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x
        
_Question = namedtuple('question',
                       'key label type default help_text validator')

def Question(key, label, answer_type='str', default=None, help_text='',
             validator=None):
    return _Question(key, label, answer_type, default, help_text, validator)


class Asker(object):
    def __init__(self, filename=''):
        if filename != '':
            with open(filename) as fp:
                data = fp.read()
                self._questions = json.loads(data,
                                             object_pairs_hook=OrderedDict)
        else:
            self._questions = None
            
        self.depends_on = {}
        self.depends_on_us = {}
    
    def ask(self, questions=None, initial_answers=None, all_questions=True,
            validators={}):
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
                if len(depends_on) != 0:
                    self.depends_on[key] = depends_on
                    for dep in depends_on:
                        if dep not in self.depends_on_us:
                            self.depends_on_us[dep] = []
                        self.depends_on_us[dep].append(key)
                
                q = Question(key, question[0], question[1],
                             default, question[3], question[4])
                self.add_question(key, q)

        result = self.go(initial_answers)
        return result

    def go(self):
        """Overridden by subclasses to ask the questions. Subclasses should
        return a dictionary of the answers"""
        
        raise NotImplemented

    def validator(self, type_validator, custom_validator=None):
        """Returns a function which validates by type first and then by a custom
        validator if one is provided
        """
        
        def validate(value):
            tv = Validators[type_validator]
            
            cv = None
            if custom_validator is not None:
                cv = Validators[custom_validator]
            
            if tv is None and cv is None:
                return value
            else:
                if tv is not None:
                    v1 = tv(value)
                else:
                    v1 = value
                    
                if cv is not None:
                    return cv(v1)
                else:
                    return v1

        return validate
    
    def _find_dependencies(self, default):
        """Returns a list of question keys the default value uses""" 
        
        f = Formatter()
        dependencies = []
        for _text, field, _format_spec, _conversion in f.parse(str(default)):
            if field is not None:
                dependencies.append(field)
        
        return dependencies
    