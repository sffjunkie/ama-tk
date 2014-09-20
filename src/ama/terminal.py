# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import readline
except ImportError:
    pass

import sys
import os.path
import getpass
import datetime
import collections

from ama import Asker
from ama.validator import Bool

if sys.version_info < (3, 0):
    input = raw_input

class TerminalException(Exception): pass


try:
    import colorama
    colorama.init()
    COLOR = True
except:
    COLOR = False


def colorize(rgb_to_intensity, color, text):
    if COLOR:
        return colorama.Style.__dict__[rgb_to_intensity.upper()] + colorama.Fore.__dict__[color.upper()] + text + colorama.Style.RESET_ALL
    else:
        return text


def create_color_func(rgb_to_intensity, name):
    def inner(text):
        return colorize(rgb_to_intensity, name, text)
    if rgb_to_intensity == 'normal':
        globals()[name] = inner
    else:
        globals()['%s_%s' % (rgb_to_intensity, name)] = inner

if COLOR:
    intensities = [x for x in colorama.Style.__dict__.keys() if x != 'RESET_ALL']
    colours = [x for x in colorama.Fore.__dict__.keys() if x != 'RESET']
else:
    intensities = ['DIM', 'NORMAL', 'BRIGHT']
    colours = ['BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE']

for rgb_to_intensity in intensities:
    for fore in colours:
        create_color_func(rgb_to_intensity.lower(), fore.lower())


class TerminalAsker(Asker):
    """Ask the questions using the terminal.

    :param title: The title to display
    :type title:     str
    :param preamble: Text to display before the questions
    :type preamble:  str
    :param filename: The filename from which to load a set of questions
    :type filename:  str
    """

    def __init__(self, title, preamble='', ds=None, json_string=None):
        Asker.__init__(self, ds, json_string)
        self._title = title
        self._preamble = preamble
        self._ask = collections.OrderedDict()
        self._encoding = getattr(sys.stdin, 'encoding', None)

    def add_question(self, key, question):
        """Add a question to the list of questions.

        Called by the :meth:`Asker.ask` method or by your code.
        """

        self._ask[key] = question

    def go(self, initial_answers):
        """Perform the question asking"""

        print(bright_green(self._title))
        print(bright_green('-' * len(self._title)))
        if self._preamble != '':
            print('\n%s\n' % self._preamble)

        result = {}
        try:
            answers = {}
            for key, question in self._ask.items():
                answer = self._ask_question(question, initial_answers, answers)
                answers[key] = answer

            result[u'answers'] = answers
            result[u'valid'] = True
            result[u'result'] = 'ok'
        except (KeyboardInterrupt, EOFError):
            try:
                result[u'result'] = 'cancel'
                print('\n[Cancelled]\n')
            except:
                pass

        return result

    def _ask_question(self, question, initial_answers, answers):
        """Ask a single question"""

        prompt_default = ''
        prompt = [question.label]
        if question.validator:
            if question.validator == 'yesno':
                if not question.label.endswith('(y/n)'):
                    prompt.append('(y/n)')

                if question.default == True or question.default == 'y':
                    prompt_default = 'y'
                elif question.default == False or question.default == 'n':
                    prompt_default = 'n'
                default = Bool()(question.default)
            else:
                try:
                    default = question.default.format(**answers)
                except:
                    default = question.default

                if question.validator == 'date' and default is None:
                    default = datetime.date.today()
                elif question.validator == 'time' and default is None:
                    default = self._default_time(question.spec)
                elif question.validator == 'color' and default is None:
                    default = self._default_color(question.spec)
                elif question.validator == 'path':
                    default = os.path.normpath(default)

                prompt_default = default

        if prompt_default:
            prompt.append('[%s]' % green(str(prompt_default)))

        validate = self.validator(question.validator,
                                  question.spec)

        prompt = ' '.join(prompt)
        while True:
            print(prompt, end=': ')
            if question.validator == 'password':
                answer = getpass.getpass('')
                confirm = question.spec is None or 'noconfirm' not in question.spec
                if confirm:
                    print('Please re-enter', end=': ')
                    answer2 = getpass.getpass('')
                else:
                    answer2 = None

                if not confirm or (confirm and answer == answer2):
                    break
                else:
                    print(bright_red('Passwords entered do not match.'))
            else:
                answer = input()

                answer = answer.strip()
                answer = self._decode_str(answer)

                if answer == '?':
                    print(question.help_text)
                    continue

                if answer == '':
                    answer = default

                try:
                    answer = validate(answer)
                except Exception as err:
                    print(bright_red('* %s\n' % str(err)))
                    continue
                break

        return answer

    def _default_time(self, value_validator):
        d = datetime.datetime.now().time()
        return d.strftime(value_validator)

    def _default_color(self, value_validator):
        if 'rgbhex' in value_validator:
            return '#ff0000'
        else:
            return 'rgb(1.0, 0.0, 0.0)'

    def _decode_str(self, value):
        if sys.version_info < (3,) and not isinstance(value, unicode):
            # for Python 2.x, try to get a Unicode string out of it
            if value.decode('ascii', 'replace').encode('ascii', 'replace') != value:
                if self._encoding:
                    value = value.decode(self._encoding)
                else:
                    print('* Note: non-ASCII characters entered '
                          'and terminal encoding unknown -- assuming '
                          'UTF-8 or Latin-1.')
                    try:
                        value = value.decode('utf-8')
                    except UnicodeDecodeError:
                        value = value.decode('latin1')

        return value
