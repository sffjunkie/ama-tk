# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Base Asker class"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import json
import gettext
from collections import OrderedDict
from string import Formatter

import ama.validator

if sys.version_info < (3, 0):
    gettext.install('ama', unicode=True) #pylint: disable=unexpected-keyword-arg
else:
    gettext.install('ama')


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
            self._questions = OrderedDict()
            questions = json.loads(data)
            for question in questions:
                self._questions[question['name']] = question
        else:
            self._questions = None

        self.depends_on = {}
        self.depends_on_us = {}

    def ask(self, questions=None, initial_answers=None, all_questions=True):
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
            questions = json.loads(questions)

        if initial_answers is None:
            initial_answers = {}

        for key, question in questions.items():
            if all_questions or key not in initial_answers:
                default = question.get('default', None)
                default = initial_answers.get(key, default)

                if default:
                    depends_on = self._find_dependencies(default)
                    if len(depends_on) != 0:
                        self.depends_on[key] = depends_on
                        for dep in depends_on:
                            if dep not in self.depends_on_us:
                                self.depends_on_us[dep] = []
                            self.depends_on_us[dep].append(key)

                    question['default'] = default

                self.add_question(key, question)

        result = self.run()

        if result['result'] == 'ok' and not all_questions:
            for key, value in initial_answers.items():
                question = questions[key]
                validator = ama.validator.get_validator(question['type'], question.get('format', None))
                result['answers'][key] = validator(value)
        return result

    def add_question(self, key, question):
        """Overridden by subclasses to add a question to the list to ask.
        Called by the :meth:`~ama.Asdker.ask` method"""

        raise NotImplementedError

    def run(self):
        """Overridden by subclasses to ask the questions. Subclasses should
        return a dictionary of the answers"""

        raise NotImplementedError

    #pylint: disable=no-self-use
    def _find_dependencies(self, default):
        """Returns a list of question keys the default value uses"""

        _formatter = Formatter()
        dependencies = []
        for _text, field, _format_spec, _conversion in _formatter.parse(str(default)):
            if field is not None:
                dependencies.append(field)

        return dependencies
