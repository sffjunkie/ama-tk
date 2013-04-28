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

from ama import Asker
from ama.tk_tooltip import ToolTip

class TkAsker(Asker):
    def __init__(self, title, preamble='', filename=''):
        Asker.__init__(self, filename)
        self._title = title
        self._preamble = preamble
        self._row = 0
        self._ask = OrderedDict()

        self._root = tk.Tk()
        self._root.title(self._title)
        
        self._edited_entry = ttk.Style()
        self._edited_entry.configure('edited.TEntry', foreground='black')
        
        self._unedited_entry = ttk.Style()
        self._unedited_entry.configure('unedited.TEntry', foreground='#666')

        header_font = font.Font(family='TkDefaultFont')
        header_font.configure(weight='bold')
        header = ttk.Label(self._root, text=self._preamble, padding=3,
                           font=header_font, wraplength=420)
        header.grid(column=0, row=0, sticky=(tk.N, tk.EW))
        
        self.content = ttk.Frame(self._root, padding=(3,3,3,3))
        self.content.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.content.columnconfigure(0, weight=1)

        self.content.columnconfigure(0, weight=0)
        self.content.columnconfigure(1, weight=1)
        self.content.columnconfigure(2, weight=0)
        self.content.columnconfigure(3, weight=0)
        
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=0)
        
        okcancel = ttk.Frame(self._root, padding=(3,3,3,3))
        
        # Swap the order of buttons for Windows
        if sys.platform.startswith('win32'):
            btn_column = (1,2)
        else:
            btn_column = (2,1)
            
        ok = ttk.Button(okcancel, text='OK', width=10, command=self._ok)
        ok.grid(column=btn_column[0], row=0, padx=(6, 0))
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
        tkq = TkQuestion(self, self._row,
                         question)
        self._ask[key] = tkq
        self._row = self._row + 1

    def current_answers(self, update_info=None):
        current_answers = {}
        for key, tkq in self._ask.items():
            current_answers[key] = tkq.value
        
        if update_info is not None:
            current_answers[update_info[0]] = update_info[1]
            
        return current_answers
    
    def update_answers(self, update_info=None):
        answers = self.current_answers(update_info)
            
        for key, tkq in self._ask.items():
            if (update_info is None or key != update_info[0]) and not tkq.edited:
                tkq.update(answers)

    def go(self, initial_answers):
        self._result = {}
        self.update_answers()
        self._root.mainloop()
        return self._result

    def _is_valid(self):
        valid = True
        for _key, question in self._ask.items():
            if not question.valid:
                valid = False
        
        return valid
    
    def _ok(self, event=None):
        self._result['valid'] = self._is_valid()
        self._result['result'] = 'ok'
        
        answers = {}
        for key, tkq in self._ask.items():
            answers[key] = tkq.validated_answer()
            
        self._result['answers'] = answers
        
        self._root.destroy()
    
    def _cancel(self, event=None):
        self._result['valid'] = False
        self._result['result'] = 'cancel'
        self._root.destroy()


class TkQuestion(object):
    def __init__(self, asker, row, question):
        self._key = question.key
        self._label = question.label
        self._type = question.type
        self._default = question.default
        if question.validator and question.validator.startswith('path('):
            self._default = os.path.normpath(self._default)
            
        self._validate = asker.validator(question.type, question.validator)

        self._var = None
        self._asker = asker
        self._row = row
        
        self._is_edited = False
        self._is_valid = True

        self.label = ttk.Label(asker.content, text=self._label)
        self.label.grid(column=0, row=self._row, sticky=(tk.N, tk.S, tk.W),
                        padx=(0,5))
        
        error_font = font.Font(family='TkFixedFont', size=10, weight='bold')
        self.info_label = ttk.Label(asker.content, font=error_font, width=2,
                                    anchor=tk.CENTER)
        self.info_label.grid(column=2, row=self._row, padx=(3,0))
        self._help_text = question.help_text
        if self._help_text != '':
            self.info_label['text'] = '?'
            self.tooltip = ToolTip(self.info_label, msg=self._help_text, delay=0.5)
        
        self._validate_entry = (asker._root.register(self._tk_validate),
                                '%P', '%V')

        current_answers = self._asker.current_answers()

        if question.validator and question.validator.startswith('path'):
            self._var = tk.StringVar()
            self.entry = ttk.Frame(asker.content)
            path_entry = ttk.Entry(self.entry, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)
            path_entry.grid(column=0, row=0, sticky=tk.EW)
            btn = ttk.Button(self.entry, text='Browse...',
                             command=self._browse_for_directory)
            btn.grid(column=1, row=0, sticky=tk.E)
            self.entry.columnconfigure(0, weight=1)
            self.entry.columnconfigure(1, weight=0)

            self.update(current_answers)
            
        elif self._type == 'str' or self._type == 'nonempty':
            self._var = tk.StringVar()
            self.entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)

            self.update(current_answers)
            
        elif self._type == 'int' or isinstance(self._type, int):
            self._var = tk.IntVar()
            self.entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)
            self.entry.configure(width=30)

            self.update(current_answers)
            
        elif self._type == 'float' or isinstance(self._type, float):
            self._var = tk.DoubleVar()
            self.entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)
            self.entry.configure(width=30)

            self.update(current_answers)
            
        elif self._type == 'bool' or self._type == 'yesno' or \
            isinstance(self._type, bool):
            self._var = tk.BooleanVar()
            self.value = self._default
            self.entry = ttk.Frame(asker.content)
            
            if self._type == 'yesno':
                text = ('Yes', 'No')
            else:
                text = ('True', 'False')
                
            y = ttk.Radiobutton(self.entry, text=text[0],
                                variable=self._var, value=True)
            y.grid(column=0, row=0, padx=(0,5))
            
            n = ttk.Radiobutton(self.entry, text=text[1],
                                variable=self._var, value=False)
            n.grid(column=1, row=0)

        elif isinstance(self._type, list):
            self._var = tk.StringVar()
            self.value = self._type[0]
            if len(self._type) <= 3:
                self.entry = ttk.Frame(asker.content)
                for idx, e in enumerate(self._type):
                    rb = ttk.Radiobutton(self.entry, text=str(e),
                                         variable=self._var, value=str(e))
                    rb.grid(column=idx, row=0, padx=(0,5))
            else:
                self.entry = ttk.Combobox(asker.content,
                                          textvariable=self._var)
                self.entry['values'] = tuple(self._type)
            
        else:
            raise ValueError(('Unable to create entry widget '
                              'for type %s') % self._type)
            
        self.entry.grid(column=1, row=self._row, sticky=tk.EW, padx=0)
        
        self.edited = self._is_edited
        asker.content.rowconfigure(self._row, weight=0)
        
    def update(self, current_answers):
        updated_answer = str(self._default).format(**current_answers)
        self.value = updated_answer
        
    def value():
        def fget(self):
            try:
                return self._var.get()
            except:
                text = self.entry.get()
                return self._validate(text)
        
        def fset(self, value):
            try:
                value = self._validate(value)
                self._var.set(value)
            except ValueError:
                self._var.set(value)
                self.valid = True
                
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
            
            if isinstance(self.entry, ttk.Entry):
                if self._is_edited:
                    self.entry['style'] = 'edited.TEntry'
                else:
                    self.entry['style'] = 'unedited.TEntry'
                    
        return locals()
    
    edited = property(**edited())
    
    def validated_answer(self):
        return self._validate(self.value)

    def _tk_validate(self, P, V):
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
                    return 0
        elif V == 'key':
            if not self.edited:
                self.edited = True
            
            self._asker.update_answers((self._key, P))

        return 1
    
    def _browse_for_directory(self, *args):
        path_entry = self.value
        path_entry = os.path.abspath(os.path.expanduser(path_entry))
        
        new_path = filedialog.askdirectory(initialdir=path_entry)
        new_path = os.path.normpath(new_path)
        
        home_path = unicode(os.path.expanduser('~'))
        current_path = unicode(os.getcwd())
        
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
