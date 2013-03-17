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

from asker import Asker
from asker.validator import Validators 

class TkAsker(Asker):
    def __init__(self, title, preamble='', filename=''):
        Asker.__init__(self, filename)
        self._title = title
        self._preamble = preamble
        self._row = 0
        self._ask = OrderedDict()

        self.root = tk.Tk()
        self.root.title(self._title)

        header_font = font.Font(family='TkDefaultFont', size=10, weight='bold')
        header = ttk.Label(self.root, text=self._preamble, padding=3, font=header_font)
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
        cancel = ttk.Button(okcancel, text='Cancel', width=10, command=self._cancel)
        cancel.grid(column=btn_column[1], row=0, padx=(6, 0))

        okcancel.columnconfigure(0, weight=1)
        okcancel.columnconfigure(1, weight=0)
        okcancel.columnconfigure(2, weight=0)
        
        okcancel.grid(column=0, row=2, sticky=(tk.E, tk.W, tk.S))
        self.root.rowconfigure(2, weight=1)
        
        #self._help_visible = False
        #self._help_window = None
        #self._help_window.withdraw()
        
        self.root.protocol('WM_DELETE_WINDOW', self._cancel)
        
        self._result = {}
    
    def add_question(self, key, question):
        tkq = TkQuestion(self, self._row,
                         question.label, question.type,
                         question.type,
                         question.default, question.help_text,
                         question.validator)
        self._ask[key] = tkq
        self._row = self._row + 1

    def go(self, initial_answers):
        self.root.mainloop()
        
        return self._result
    
    def _ok(self, event=None):
        self._result['result'] = 'ok'
        
        answers = {}
        for key, tkq in self._ask.items():
            answer = Validators[tkq._type](tkq.value.get())
            answers[key] = answer
            
        self._result['answers'] = answers
        
        self.root.destroy()
    
    def _cancel(self, event=None):
        self._result['result'] = 'cancel'
        self.root.destroy()
    
    def toggle_help(self, event):
        if self._help_visible:
            try:
                self._asker._help_window.withdraw()
            except:
                pass
            self._help_visible = False
        else:
            self._help_window.deiconify()
            self._help_visible = True
            
    def _help_closed(self):
        self._help_window.destroy()
        self._help_window = None
        self._help_visible = False


class TkQuestion(object):
    def __init__(self, asker, row, label, type_, valid, default, help_text='', validator=None):
        self.value = None
        self._asker = asker
        self._row = row
        self._type = type_

        self.label = ttk.Label(asker.content, text=label)
        self.label.grid(column=0, row=self._row*2, sticky=(tk.N, tk.S, tk.W), padx=(0,5))

        if type_ == 'str':
            self.value = tk.StringVar()
            self.value.set(default)
            self.entry = ttk.Entry(asker.content, textvariable=self.value)
            
        elif type_ == 'bool' or type_ == 'yesno' or isinstance(valid, bool):
            self.value = tk.BooleanVar()
            self.entry = ttk.Frame(asker.content)
            y = ttk.Radiobutton(self.entry, text='Yes', variable=self.value, value=True)
            y.grid(column=0, row=0, padx=(0,5))
            n = ttk.Radiobutton(self.entry, text='No', variable=self.value, value=False)
            self.value.set(Validators['yesno'](default))
            n.grid(column=1, row=0)
            
        elif type_ == 'int' or isinstance(valid, int):
            self.value = tk.IntVar()
            self.entry = ttk.Entry(asker.content)
            self.entry.configure(width=30)
            
        elif isinstance(valid, list):
            self.value = tk.StringVar()
            if len(valid) <= 3:
                self.entry = ttk.Frame(asker.content)
                for idx in range(len(valid)):
                    e = valid[idx]
                    rb = ttk.Radiobutton(self.entry, text=str(e), variable=self.value, value=str(e))
                    rb.grid(column=idx, row=0, padx=(0,5))
            else:
                self.entry = ttk.Combobox(asker.content, textvariable=self.value)
                self.entry['values'] = tuple(valid)
            self.value.set(str(valid[0]))
            
        else:
            raise ValueError('Unable to create entry widget valid=%s' % valid)
            
        self.entry.grid(column=1, row=self._row*2, sticky=tk.EW)
        
        error_font = font.Font(family='TkFixedFont', size=10, weight='bold')
        self.err_label = ttk.Label(asker.content, font=error_font, text=' ', width=1, foreground='red')
        self.err_label.grid(column=2, row=self._row*2)
        
        #if help_text != '':
        #    self.button = ttk.Button(asker.content, text='?', width=4)
        #    self.button.grid(column=3, row=self._row*2, sticky=(tk.N, tk.S, tk.E), padx=(5,0))
        #    self.button.bind('<Button-1>', self.toggle_help)
        
        asker.content.rowconfigure(self._row, weight=0)
        asker.content.rowconfigure((self._row*2) + 1, weight=1)
    
    def toggle_help(self, event):
        self._asker.toggle_help(event)
        
    def invalid(self, invalid=True):
        if invalid:
            self.err_label['text'] = '*'
        else:
            self.err_label['text'] = ' '   
    
    def _validate_integer(self, P, S, W):
        return True

