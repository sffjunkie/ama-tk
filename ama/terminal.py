# Copyright 2009-2014, Simon Kennedy, code@sffjunkie.co.uk

try:
    import readline
except ImportError:
    pass

try:
    # Try assigning the Python 2 version of the input function
    input = raw_input
except:
    pass

import os.path
import collections 

from ama import Asker
from ama.validator import validate_bool

try:
    import colorama
    colorama.init(autoreset=True)
    COLOR = True
except:
    COLOR = False

    
def colorize(rgb_to_intensity, color, text):
    if COLOR:
        return colorama.Style.__dict__[rgb_to_intensity.upper()] + colorama.Fore.__dict__[color.upper()] + text
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
    intensities = [x for x in colorama.Style.__dict__.keys() if x!='RESET_ALL']
    colours = [x for x in colorama.Fore.__dict__.keys() if x!='RESET']
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
    
    def add_question(self, key, question):
        """Add a question to the list of questions.
        
        Called by the :meth:`Asker.ask` method or by your code.
        """
        
        self._ask[key] = question
    
    def go(self, initial_answers):
        """Perform the question asking"""
        
        print(bright_green(self._title))
        print(bright_green('-'*len(self._title)))
        if self._preamble != '':
            print('\n%s' % self._preamble)
        print('\n')
           
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
                print('\n[Interrupted]\n')
            except:
                pass
            
        return result

    def _ask_question(self, question, initial_answers, answers):
        """Ask a single question"""
        
        prompt_tail = ''
        if question.validator == 'yesno':
            if not question.label.endswith(' (y/n)'):
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
            
            if question.validator and question.validator.startswith('path'):
                default = os.path.normpath(default)
            
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
                validate = self.validator(question.type, question.validator)
                answer = validate(answer)
            except Exception as err:
                print(bright_red('* %s\n' % str(err)))
                print(question.help_text)
                continue
            break
    
        return answer
