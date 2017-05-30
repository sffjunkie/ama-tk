# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Terminal based Asker"""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import readline #pylint: disable=unused-import
except ImportError:
    pass

import sys
import os.path
import getpass
import datetime
import collections

from ama import Asker
import ama.validator

if sys.version_info < (3, 0):
    input = raw_input  #pylint: disable=redefined-builtin,invalid-name,undefined-variable


try:
    import colorama
    colorama.init()
    COLOR = True
except ImportError:
    COLOR = False


def create_color_func(intensity, color):
    def inner(text):
        if COLOR:
            return colorama.Style.__dict__[intensity.upper()] + \
                colorama.Fore.__dict__[color.upper()] + \
                text + colorama.Style.RESET_ALL
        else:
            return text
    if intensity == 'normal':
        globals()['_%s' % color] = inner
    else:
        globals()['_%s_%s' % (intensity, color)] = inner


_intensities = [x for x in colorama.Style.__dict__.keys() if x != 'RESET_ALL']
_colours = [x for x in colorama.Fore.__dict__.keys() if x != 'RESET']

for _intensity in _intensities:
    for _fore in _colours:
        create_color_func(_intensity.lower(), _fore.lower())


class TerminalAsker(Asker):
    """Ask the questions using the terminal.

    :param title:       The title to display
    :type title:        str
    :param preamble:    Text to display before the questions
    :type preamble:     str
    :param ds:          The data stream from which to load a set of questions
    :type ds:           file
    :param json_string: JSON string to parse
    :type json_string:  str
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

    def run(self):
        """Perform the question asking"""

        print(_bright_green(self._title))
        print(_bright_green('-' * len(self._title)))
        if self._preamble != '':
            print('\n%s\n' % self._preamble)

        result = {}
        try:
            answers = {}
            for key, question in self._ask.items():
                answer = self._ask_question(question, answers)
                answers[key] = answer

            result[u'answers'] = answers
            result[u'valid'] = True
            result[u'result'] = 'ok'
        except (KeyboardInterrupt, EOFError):
            try:
                result[u'result'] = 'cancel'
                print('\n[Cancelled]\n')
            except Exception: # pylint: disable=broad-except
                pass

        return result

    def _ask_question(self, question, answers):
        """Ask a single question"""

        prompt_default = ''
        message = question['message']
        prompt = [_bright_green('[?]'), message]
        default = question.get('default', None)
        if default:
            if question['type'] in ['yesno', 'confirm']:
                if not message.endswith('(y/n)'):
                    prompt.append('(y/n)')

                if default in [True, 'y', 'Y']:
                    default = True
                    prompt_default = 'y'
                elif default in [False, 'n', 'N']:
                    default = False
                    prompt_default = 'n'
            else:
                try:
                    default = question['default'].format(**answers)
                except (KeyError, AttributeError):
                    default = question['default']

                prompt_default = default
        else:
            format_ = question.get('format', None)
            if question['type'] == 'date' and default is None:
                default = _default_date(format_)
            elif question['type'] == 'time' and default is None:
                default = _default_time(format_)
            elif question['type'] == 'color' and default is None:
                default = _default_color(format_)
            elif question['type'] == 'path':
                default = os.path.normpath(default)

            prompt_default = default

        if prompt_default:
            prompt.append('[%s]' % _green(str(prompt_default)))

        validator = ama.validator.get_validator(question['type'], question.get('format', None))

        prompt = ' '.join(prompt)
        while True:
            print(prompt, end=' ')
            if question['type'] == 'password':
                answer = getpass.getpass('')
                confirm = ('format' in question and 'noconfirm' not in question['format']) or True
                if confirm:
                    print('Please re-enter', end=': ')
                    answer2 = getpass.getpass('')
                else:
                    answer2 = None

                if not confirm or (confirm and answer == answer2):
                    break
                else:
                    print(_bright_red('Passwords entered do not match.'))
            else:
                answer = input()

                answer = answer.strip()
                answer = self._decode_str(answer)

                if answer == '?':
                    print(question['help'])
                    continue

                if answer == '':
                    answer = default

                try:
                    answer = validator(answer)
                except (ValueError, TypeError) as err:
                    print(_bright_red('* %s\n' % str(err)))
                    continue
                break

        return answer

    def _decode_str(self, value):
        if sys.version_info < (3,) and not isinstance(value, unicode): # pylint: disable=undefined-variable
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


def _default_date(value_validator):
    today = datetime.date.today()
    if value_validator:
        return today.strftime(value_validator)
    else:
        return today


def _default_time(value_validator):
    now = datetime.datetime.now().time()
    if value_validator:
        return now.strftime(value_validator)
    else:
        return now


def _default_color(value_validator):
    if value_validator and 'rgbhex' in value_validator:
        return '#ff0000'
    else:
        return 'rgb(1.0, 0.0, 0.0)'
