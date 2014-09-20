# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import json
import gettext
from string import Formatter
from collections import namedtuple, OrderedDict

install_args = {}
if sys.version_info < (3, 0):
    install_args['unicode'] = True
gettext.install('ama', **install_args)

import ama.validator

_Question = namedtuple('question',
                       ('key label help_text default '
                        'validator spec'))

def Question(key, label, help_text='', default=None, validator='str', spec=None):
    return _Question(key, label, help_text, default, validator, spec)


class Asker(object):
    """An object which mediates the question asking.

    :param ds: A datastream to read the questions from
    :type ds:  Any object with a read metod
    :param json_string: A JSON formatted string to load the questions from
    :type json_string: str
    """

    def __init__(self, ds=None, json_string=None):
        data = None
        if ds:
            data = ds.read()
        elif json_string:
            data = json_string

        if data:
            self._questions = json.loads(data, object_pairs_hook=OrderedDict)
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

        if not isinstance(questions, OrderedDict):
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

                q = Question(key,
                             label=question[0],
                             help_text=question[1],
                             default=default,
                             validator=question[3],
                             spec=question[4])
                self.add_question(key, q)

        result = self.go(initial_answers)

        if result['result'] == 'ok' and all_questions == False:
            for key, value in initial_answers.items():
                q = questions[key]
                v = ama.validator.get_validator(q[3], q[4])
                result['answers'][key] = v(value)
        return result

    def add_question(self):
        """Overridden by subclasses to add a question to the list to ask.
        Called by the :meth:`~ama.Asdker.ask` method"""

        raise NotImplemented

    def go(self):
        """Overridden by subclasses to ask the questions. Subclasses should
        return a dictionary of the answers"""

        raise NotImplemented

    def _find_dependencies(self, default):
        """Returns a list of question keys the default value uses"""

        f = Formatter()
        dependencies = []
        for _text, field, _format_spec, _conversion in f.parse(str(default)):
            if field is not None:
                dependencies.append(field)

        return dependencies
