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

from ama import Asker
from ama.validator import Validators
from ama.tk_tooltip import ToolTip

class TkAsker(Asker):
    def __init__(self, title, preamble='', filename=''):
        Asker.__init__(self, filename)
        self._title = title
        self._preamble = preamble
        self._row = 0
        self._ask = OrderedDict()

        self.root = tk.Tk()
        self.root.title(self._title)
        
        self._edited_entry = ttk.Style()
        self._edited_entry.configure('edited.TEntry', foreground='black')
        
        self._unedited_entry = ttk.Style()
        self._unedited_entry.configure('unedited.TEntry', foreground='#666')

        header_font = font.Font(family='TkDefaultFont')
        header_font.configure(weight='bold')
        header = ttk.Label(self.root, text=self._preamble, padding=3,
                           font=header_font, wraplength=420)
        header.grid(column=0, row=0, sticky=(tk.N, tk.EW))
        
        self.content = ttk.Frame(self.root, padding=(3,3,3,3))
        self.content.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.content.columnconfigure(0, weight=1)

        self.content.columnconfigure(0, weight=0)
        self.content.columnconfigure(1, weight=1)
        self.content.columnconfigure(2, weight=0)
        self.content.columnconfigure(3, weight=0)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=0)
        
        okcancel = ttk.Frame(self.root, padding=(3,3,3,3))
        
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
        self.root.rowconfigure(2, weight=1)
        
        self.root.protocol('WM_DELETE_WINDOW', self._cancel)
        
        if sys.platform.startswith('darwin'):
            self.root.createcommand("::tk::mac::Quit", self._cancel)
    
    def add_question(self, key, question):
        tkq = TkQuestion(self, self._row,
                         question)
        self._ask[key] = tkq
        self._row = self._row + 1
    
    def update_answers(self, update_info=None):
        current_answers = {}
        for key, tkq in self._ask.items():
            current_answers[key] = tkq.value
        
        if update_info is not None:
            current_answers[update_info[0]] = update_info[1]
            
        for key, tkq in self._ask.items():
            if update_info is None or key != update_info[0]:
                tkq.update(current_answers)

    def go(self, initial_answers):
        self._result = {}
        self.update_answers()
        self.root.mainloop()
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
        
        self.root.destroy()
    
    def _cancel(self, event=None):
        self._result['valid'] = False
        self._result['result'] = 'cancel'
        self.root.destroy()


class TkQuestion(object):
    def __init__(self, asker, row, question):
        self._key = question.key
        self._label = question.label
        self._type = question.type
        self._default = question.default
        self._validate = asker.validator(question.type, question.validator)
        
        self._var = None
        self._asker = asker
        self._row = row
        
        self._is_edited = False
        self._is_valid = True

        self.label = ttk.Label(asker.content, text=self._label)
        self.label.grid(column=0, row=self._row, sticky=(tk.N, tk.S, tk.W),
                        padx=(0,5))
        
        self._validate_entry = (asker.root.register(self._tk_validate),
                                '%P', '%V')

        if self._type == 'str' or self._type == 'nonempty':
            self._var = tk.StringVar()
            self.entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)

            self.value = self._default
            
        elif self._type == 'int' or isinstance(self._type, int):
            self._var = tk.IntVar()
            self.value = Validators['int'](self._default)
                
            self.entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)
            self.entry.configure(width=30)
            
        elif self._type == 'float' or isinstance(self._type, float):
            self._var = tk.DoubleVar()
            self.value = Validators['float'](self._default)
                
            self.entry = ttk.Entry(asker.content, textvariable=self._var,
                                   validate='all',
                                   validatecommand=self._validate_entry)
            self.entry.configure(width=30)
            
        elif self._type == 'bool' or self._type == 'yesno' or \
            isinstance(self._type, bool):
            self._var = tk.BooleanVar()
            self.entry = ttk.Frame(asker.content)
            y = ttk.Radiobutton(self.entry, text='Yes',
                                variable=self._var, value=True)
            y.grid(column=0, row=0, padx=(0,5))
            
            n = ttk.Radiobutton(self.entry, text='No',
                                variable=self._var, value=False)
            n.grid(column=1, row=0)
            
            self.value = Validators['yesno'](self._default)

        elif isinstance(self._type, list):
            self._var = tk.StringVar()
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
                
            self.value = str(self._type[0])
            
        else:
            raise ValueError(('Unable to create entry widget '
                              'for type %s') % self._type)
            
        self.entry.grid(column=1, row=self._row, sticky=tk.EW)
        
        error_font = font.Font(family='TkFixedFont', size=10, weight='bold')
        self.info_label = ttk.Label(asker.content, font=error_font, width=2, anchor=tk.CENTER)
        self.info_label.grid(column=2, row=self._row, padx=(3,0))
        self._help_text = question.help_text
        if self._help_text != '':
            self.info_label['text'] = '?'
            self.tooltip = ToolTip(self.info_label, msg=self._help_text, delay=0.5)
        
        self.edited = self._is_edited
        self.valid = self._is_valid
        
        asker.content.rowconfigure(self._row, weight=0)
        
    def update(self, current_answers):
        try:
            updated_answer = str(self._default).format(**current_answers)
            value = self._validate(updated_answer)
            self._var.set(value)
        except:
            pass
        
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
            except:
                raise ValueError
                
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

