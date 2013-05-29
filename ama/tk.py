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
from datetime import date, datetime
from collections import OrderedDict

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

try:
    from tkinter import font
except ImportError:
    import tkFont as font

try:
    from tkinter import ttk
except ImportError:
    import ttk
    
try:
    from tkinter import filedialog
except ImportError:
    import tkFileDialog as filedialog

from ama import Asker, u
from ama.tk_tooltip import ToolTip

class TkAsker(Asker):
    """Displays a Tk window containing the questins to be asked.
    
    :param title: The title to display
    :type title:     str
    :param preamble: Text to display before the questions
    :type preamble:  str
    :param filename: The filename from which to load a set of questions
    :type filename:  str
    :param allow_invlaid: If True then invalid answers are accepted.
                          If False then you can't close the window until
                          all answers are valid.
    :type allow_invlaid:  bool
    """
    
    def __init__(self, title, preamble='', filename='', allow_invalid=True):
        Asker.__init__(self, filename)
        self._title = title
        self._preamble = preamble
        self._allow_invalid = allow_invalid
        self._row = 0
        self._ask = OrderedDict()

        self._root = tk.Tk()
        self._root.title(self._title)
        
        self._edited_entry = ttk.Style()
        self._edited_entry.configure('edited.TEntry', foreground='black')
        
        self._unedited_entry = ttk.Style()
        self._unedited_entry.configure('unedited.TEntry', foreground='#666')

        header_font = font.Font(family='TkDefaultFont', weight='bold')
        header = ttk.Label(self._root, text=self._preamble, padding=3,
                           font=header_font, wraplength=420)
        header.grid(column=0, row=0, sticky=(tk.N, tk.EW))
        
        self.content = ttk.Frame(self._root, padding=(3,3,3,3))
        self.content.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.content.columnconfigure(0, weight=0)
        self.content.columnconfigure(1, weight=1)
        self.content.columnconfigure(2, weight=0)
        
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=0)
        
        okcancel = ttk.Frame(self._root, padding=(3,3,3,3))
        
        # Swap the order of buttons for Windows
        if sys.platform.startswith('win32'):
            btn_column = (1,2)
        else:
            btn_column = (2,1)
            
        self.ok_btn = ttk.Button(okcancel, text='OK', width=10, command=self._ok)
        self.ok_btn.grid(column=btn_column[0], row=0, padx=(6, 0))
        cancel = ttk.Button(okcancel, text='Cancel', width=10,
                            command=self._cancel)
        cancel.grid(column=btn_column[1], row=0, padx=(6, 0))

        okcancel.columnconfigure(0, weight=1)
        okcancel.columnconfigure(1, weight=0)
        okcancel.columnconfigure(2, weight=0)
        
        okcancel.grid(column=0, row=2, sticky=(tk.E, tk.W, tk.S))
        self._root.rowconfigure(2, weight=1)
        
        self._root.protocol('WM_DELETE_WINDOW', self._cancel)
        
        if sys.platform.startswith('darwin'):
            self._root.createcommand("::tk::mac::Quit", self._cancel)
    
    def add_question(self, key, question):
        """Add a question to the list of questions.
        
        Called by the :meth:`Asker.ask` method or by your code.
        """
        
        tkq = TkQuestion(self, self._row,
                         question)
        self._ask[key] = tkq
        self._row = self._row + 1

    def go(self, initial_answers):
        """Perform the question asking by displaying in a Tkinter window"""
        
        self._result = {}
        self.update_answers()
        self._root.mainloop()
        return self._result

    def current_answers(self, update_info=None):
        """Return a dictionary of the current answers to the questions.
        
        :param update_info:   A 2 element tuple containing the key of a
                              question and its new value.
        :type update_info:    tuple
        """
        
        current_answers = {}
        for key, tkq in self._ask.items():
            current_answers[key] = tkq.value
        
        if update_info is not None:
            current_answers[update_info[0]] = update_info[1]
            
        return current_answers
    
    def update_answers(self, update_info=None):
        """Update all unedited answers with the values from the other answers"""
        
        answers = self.current_answers(update_info)
            
        for key, tkq in self._ask.items():
            if (update_info is None or key != update_info[0]) and \
            (not tkq.edited or key == update_info[0]):
                tkq.update(answers)

    def check_invalid(self):
        """If we don't allow invalid answers then disable the OK button if
        we have any.
        """
        
        if not self._allow_invalid and not self._is_valid():
            self.ok_btn.state(['disabled'])
        else:
            self.ok_btn.state(['!disabled'])
            
        self.ok_btn.update_idletasks()

    def _is_valid(self):
        """Check if all the answers are valid."""
        
        for _key, question in self._ask.items():
            if not question.valid:
                return False
        
        return True
    
    def _ok(self, event=None):
        """Respond to the OK button being pressed."""
        
        self._result['valid'] = self._is_valid()
        self._result['result'] = 'ok'
        
        answers = {}
        for key, tkq in self._ask.items():
            answers[key] = tkq.value
            
        self._result['answers'] = answers
        
        self._root.destroy()
    
    def _cancel(self, event=None):
        """Respond to the Cancel button being pressed."""
        
        self._result['valid'] = False
        self._result['result'] = 'cancel'
        self._root.destroy()


class TkQuestion(object):
    """Displays the controls for a single question."""
    
    def __init__(self, asker, row, question):
        self._key = question.key
        self._label = question.label
        self._type = question.type
        self._default = question.default
        self._validator = question.validator
        if self._validator and self._validator.startswith('path'):
            self._default = os.path.normpath(self._default)
            
        self._validate = asker.validator(self._type, self._validator)

        self._dont_update = ['date', 'time']

        self._var = None
        self._asker = asker
        self._row = row
        self._entry = None
        
        self._is_edited = False
        self._is_valid = True

        self.label = ttk.Label(asker.content, text=self._label)
        self.label.grid(column=0, row=self._row, sticky=(tk.N, tk.S, tk.W),
                        padx=(0,5))
        
        s = ttk.Style()
        s.configure('error.TLabel', font='TkFixedFont 10 bold')
        self.info_label = ttk.Label(asker.content, width=2,
                                    anchor=tk.CENTER, style='error.TLabel')
        self.info_label.grid(column=2, row=self._row, padx=(3,0))
        self._help_text = question.help_text
        if self._help_text != '':
            self.info_label['text'] = '?'
            self.tooltip = ToolTip(self.info_label, msg=self._help_text, delay=0.5)
        
        self._validate_entry = (asker._root.register(self._tk_validate),
                                '%P', '%V')

        current_answers = self._asker.current_answers()

        if self._validator and self._validator.startswith('path'):
            self._var = tk.StringVar()
            frame = self._create_entry_with_button(asker.content,
                'Browse...',
                self._browse_for_directory)

            self.update(current_answers)
            
        elif self._type == 'str':
            self._var = tk.StringVar()
            self._entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)
            frame = self._entry
            self.update(current_answers)
            
        elif self._type == 'int' or isinstance(self._type, int):
            self._var = tk.IntVar()
            self._entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)
            self._entry.configure(width=30)
            frame = self._entry

            self.update(current_answers)
            
        elif self._type == 'float' or isinstance(self._type, float):
            self._var = tk.DoubleVar()
            self._entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)
            self._entry.configure(width=30)
            frame = self._entry

            self.update(current_answers)
            
        elif self._type == 'bool' or self._validator == 'yesno' or \
            isinstance(self._type, bool):
            self._var = tk.BooleanVar()
            self.value = self._default
            frame = ttk.Frame(asker.content)
            
            if self._validator == 'yesno':
                text = ('Yes', 'No')
            else:
                text = ('True', 'False')
                
            y = ttk.Radiobutton(frame, text=text[0],
                                variable=self._var, value=True)
            y.grid(column=0, row=0, padx=(0,5))
            
            n = ttk.Radiobutton(frame, text=text[1],
                                variable=self._var, value=False)
            n.grid(column=1, row=0)

        elif isinstance(self._type, list):
            self._var = tk.StringVar()
            self.value = self._type[0]
            if len(self._type) <= 3:
                frame = ttk.Frame(asker.content)
                for idx, e in enumerate(self._type):
                    rb = ttk.Radiobutton(frame, text=str(e),
                                         variable=self._var, value=str(e))
                    rb.grid(column=idx, row=0, padx=(0,5))
            else:
                self._entry = ttk.Combobox(asker.content,
                                          textvariable=self._var)
                self._entry['values'] = tuple(self._type)
                frame = self._entry
            
        else:
            raise ValueError(('Unable to create _entry widget '
                              'for type %s') % self._type)
            
        frame.grid(column=1, row=self._row, sticky=tk.EW, padx=0)
        
        self.edited = self._is_edited
        asker.content.rowconfigure(self._row, weight=0)
        
    def update(self, current_answers):
        """Update our unedited value with the other answers."""
        if self._validator is None:
            do_update = True
        else:
            name = self._validator.split('(')[0]
            do_update =  name not in self._dont_update
            
        if do_update:
            updated_answer = str(self._default).format(**current_answers)
            self.value = updated_answer
        
    def value():
        def fget(self):
            try:
                return self._validate(self._var.get())
            except:
                return self._entry.get()
        
        def fset(self, value):
            try:
                value = self._validate(value)
                self._var.set(value)
                self.valid = True
            except ValueError:
                self._var.set(value)
                self.valid = False
                
        return locals()
    
    value = property(**value())

    def valid():
        def fget(self):
            return self._is_valid
        
        def fset(self, value):
            self._is_valid = bool(value)
            if self._is_valid:
                if self._help_text != '':
                    self.info_label['text'] = '?'
                self.info_label['foreground'] = 'black'
            else:
                self.info_label['text'] = '!'
                self.info_label['foreground'] = 'red'
                
        return locals()

    valid = property(**valid())
        
    def edited():
        def fget(self):
            return self._is_edited
        
        def fset(self, value):
            self._is_edited = bool(value)
            
            if isinstance(self._entry, ttk.Entry):
                if self._is_edited:
                    self._entry['style'] = 'edited.TEntry'
                else:
                    self._entry['style'] = 'unedited.TEntry'
                    
        return locals()
    
    edited = property(**edited())
    
    def _tk_validate(self, P, V):
        rtn = 1
        if V == 'focusout':
            if P.strip() == '':
                self.valid = True
                self.edited = False
            else:
                try:
                    _value = self._validate(P)
                    self.valid = True
                except:
                    self.valid = False
                    rtn = 0
                
            self._asker.check_invalid()
        elif V == 'key':
            if not self.edited:
                self.edited = True
            
            self._asker.update_answers((self._key, P))

        return rtn

    def _create_entry_with_button(self, master, text, command):
        frame = ttk.Frame(master)
        
        self._entry = ttk.Entry(frame, textvariable=self._var, 
            validate='all', 
            validatecommand=self._validate_entry)
        self._entry.grid(column=0, row=0, sticky=tk.EW)
        
        btn = ttk.Button(frame, text=text, 
            command=command)
        btn.grid(column=1, row=0, sticky=tk.E)
        
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
        
        return frame
    
    def _browse_for_directory(self, *args):
        path_entry = self.value
        path_entry = os.path.abspath(os.path.expanduser(path_entry))
        
        new_path = filedialog.askdirectory(initialdir=path_entry)
        new_path = os.path.normpath(new_path)
        
        home_path = u(os.path.expanduser('~'))
        current_path = u(os.getcwd())
        
        if new_path == home_path:
            new_path = '~'
        elif new_path.startswith(home_path):
            new_path = os.path.join('~', new_path[len(home_path)+1:])
        elif new_path == current_path:
            new_path = '.'
        elif new_path.startswith(current_path):
            new_path = os.path.join('.', new_path[len(current_path)+1:])
            
        self.value = new_path
        self._asker.update_answers((self._key, new_path))
