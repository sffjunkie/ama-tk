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
import locale
import datetime

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
    import babel.dates
    USE_BABEL = True
except:
    USE_BABEL = False

from ama.validator import DEFAULT_TIME_FORMAT


class TimeEntry(ttk.Frame):
    def __init__(self, asker, time_format=DEFAULT_TIME_FORMAT, start_time=None):
        self._asker = asker
        ttk.Frame.__init__(self, self._asker.content)
        
        self.time_format = time_format
        
        if time_format.find(':') != -1:
            separator = ':'
        elif time_format.find('-') != -1:
            separator = '-'
        else:
            raise ValueError("Don't know how to handle time format %s" % time_format)

        elems = time_format.split(separator)
        
        if len(elems) < 2:
            raise ValueError("Don't know how to handle time format %s" % time_format)
        
        if start_time is None:
            start_time = datetime.time(9,0,0)
           
        self._hour_var = tk.IntVar()
        self._hour = ttk.Combobox(self, textvariable=self._hour_var, width=3)
        self._hour['values'] = map(lambda x: '%02d' % x, range(24))
        self._hour.grid(row=0, column=0)
        
        l = ttk.Label(self, text=separator, width=1, justify=tk.CENTER)
        l.grid(row=0, column=1)
        
        self._minute_var = tk.IntVar()
        self._minute = ttk.Combobox(self, textvariable=self._minute_var,
                                    width=3)
        self._minute['values'] = map(lambda x: '%02d' % x, range(60))
        self._minute.grid(row=0, column=2)
        
        self._use_second = False
        if len(elems) == 3:
            self._use_second = True
            l = ttk.Label(self, text=separator, width=1, justify=tk.CENTER)
            l.grid(row=0, column=3)
        
            self._second_var = tk.IntVar()
            self._second = ttk.Combobox(self, textvariable=self._second_var,
                                        width=3)
            self._second['values'] = map(lambda x: '%02d' % x, range(60))
            self._second.grid(row=0, column=4)
        else:
            btn = ttk.Button(self, text='Select...', command=self._select_time)
            btn.grid(row=0, column=5, sticky=tk.E)
            
        self.set(start_time)
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=1)
        
    def get(self):
        h = self._hour_var.get()
        m = self._minute_var.get()
        if self._use_second:
            s = self._second_var.get()
        else:
            s = 0
        
        if h == '' or m == '' or s == '':
            return None
        else:
            return datetime.time(hour=int(h),
                                 minute=int(m),
                                 second=int(s))

    def set(self, value):
        if not isinstance(value, (datetime.time, datetime.datetime)):
            value = datetime.datetime.strptime(value, self.time_format)
            
        self._hour_var.set('%02d' % value.hour)
        self._minute_var.set('%02d' % value.minute)
        if self._use_second:
            self._second_var.set('%02d' % value.second)

    def _select_time(self):
        if self._use_second:
            second = self._second_var.get()
        else:
            second = 0
            
        t = datetime.time(hour=self._hour_var.get(),
                          minute=self._minute_var.get(),
                          second=second)
            
        dlg = TimeDialog(self._asker._root, 'Select a Time...', start_time=t)
        self._asker._root.wait_window(dlg._top)
        new_time = dlg.time
        if new_time != None:
            self.value = new_time
            self.edited = True


class TimeDialog(object):
    def __init__(self, master, title, time_format=DEFAULT_TIME_FORMAT,
                 start_time=None):
        self._master = master
        self._top = tk.Toplevel(self._master)
        self._top.title(title)
        
        self._selector = ButtonTimeSelector(self._top, start_time)
            
        self._selector.grid(row=0, column=0, sticky=tk.NSEW)
        self._top.columnconfigure(0, weight=1)
        
        okcancel = ttk.Frame(self._top, padding=(3,3,3,3))
        
        # Swap the order of buttons for Windows
        if sys.platform.startswith('win32'):
            btn_column = (1,2)
        else:
            btn_column = (2,1)
            
        self.ok_btn = ttk.Button(okcancel, text='OK', width=10,
                                 command=self._ok)
        self.ok_btn.grid(column=btn_column[0], row=0, padx=(3, 0))
        cancel = ttk.Button(okcancel, text='Cancel', width=10,
                            command=self._cancel)
        cancel.grid(column=btn_column[1], row=0, padx=(3, 0))

        okcancel.columnconfigure(0, weight=1)
        okcancel.columnconfigure(1, weight=0)
        okcancel.columnconfigure(2, weight=0)
        
        okcancel.grid(column=0, row=2, sticky=(tk.E, tk.W, tk.S))
        
        self.value = None
        self._top.bind('<Escape>', self._cancel)
        self._top.protocol('WM_DELETE_WINDOW', self._cancel)
        self._top.lift()
        self._top.grab_set()

    def _ok(self, event=None):
        self.time = self._selector.get()
        self._top.grab_release()
        self._top.destroy()
    
    def _cancel(self, event=None):
        self.time = None
        self._top.grab_release()
        self._top.destroy()


class ButtonTimeSelector(ttk.Frame):
    def __init__(self, master, start_time=None):
        """Create a Time widget"""
        
        self._master = master
        ttk.Frame.__init__(self, master)
        
        if start_time is None:
            self._time = datetime.datetime.now().time()
        else:
            self._time = start_time
        
        button_labels = [['7', '8', '9'],
                         ['4', '5', '6'],
                         ['1', '2', '3'],
                         [':00', '0', ':30']]
        self._buttons = []
        
        def _button_command(label):
            def pressed(event=None):
                self.time_value.append(label)
                self._buttons[3][0].state(['!disabled'])
                self._buttons[3][2].state(['!disabled'])
                
                self._set_number_state()
                
            return pressed

        style = ttk.Style()
        style.configure('time.TLabel', foreground='#041')
        
        frame = ttk.Frame(self)
        
        self.time_value = TimeVar(value='00:00')
        self.time_entry = ttk.Entry(frame,
                                    textvariable=self.time_value,
                                    style='time.TLabel',
                                    justify=tk.CENTER,
                                    state=['readonly'])
        self.time_entry.grid(row=0, column=1)
        
        clear_btn = ttk.Button(frame, text='C', width=2, command=self.clear)
        clear_btn.grid(row=0, column=0)
        
        frame.columnconfigure(0, weight=0)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=0)
        frame.grid(row=0, column=0, sticky=(tk.N, tk.EW), pady=(0,3))
                
        for row_number, row_labels in enumerate(button_labels):
            frame = ttk.Frame(self)
            button_row = []
            
            for button_number, label in enumerate(row_labels):
                button = ttk.Button(frame, text=label,
                                    command=_button_command(label),
                                    width=5)
                button.grid(row=0, column=button_number, sticky=tk.EW)
                button_row.append(button)
                
            self._buttons.append(button_row)
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(2, weight=1)
            frame.grid(row=row_number+1, column=0, sticky=tk.EW)

        self._buttons[3][0].state(['disabled'])
        self._buttons[3][2].state(['disabled'])

        self.grid(row=0, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)
        self.columnconfigure(0, weight=1)

        for key in map(str,range(10)):
            self._master.bind(key, _button_command(key))

        #self._master.bind('<BackSpace>', self.undo)
        self._master.bind('c', self.clear)
        
        self._undo = []

    def undo(self, event=None):
        pass
        #self.time_value.undo()

    def clear(self, event=None):
        self.time_value.set('')
        self._set_number_state()
        self._buttons[3][0].state(['disabled'])
        self._buttons[3][2].state(['disabled'])
        
    def get(self):
        return self.time_value.get()
    
    def set(self, value):
        self.time_value.set(value)
        
    def _set_number_state(self):
        if self.time_value.allow_append():
            state = '!disabled'
        else:
            state = 'disabled'
        
        # 1-9    
        for row in range(3):
            for column in range(3):
                self._buttons[row][column].state([state])

        # 0                
        self._buttons[3][1].state([state])
