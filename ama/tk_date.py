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
import datetime
import calendar

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

from ama.validator import DEFAULT_DATE_FORMAT


class DateEntry(ttk.Frame):
    """A date entry widget containing text entry boxes for year, month and day
    and a button to display a date selection dialog
    """
    
    def __init__(self, asker, date_format=DEFAULT_DATE_FORMAT,
                 start_date=None):
        self._asker = asker
        ttk.Frame.__init__(self, self._asker.content)
        
        self.format = date_format
        if date_format.find('-') != -1:
            separator = '-'
        elif date_format.find('/') != -1:
            separator = '/'
        else:
            raise ValueError('Invalid date date_format %s specified' % \
                             date_format)

        elems = date_format.split(separator)
            
        self._calendar = calendar.TextCalendar()
    
        year_col = -1
        month_col = -1
        day_col = -1
        for pos, elem in enumerate(elems):
            if elem == '%Y':
                year_col = pos
            elif elem == '%y':
                year_col = pos
            elif elem == '%m':
                month_col = pos
            elif elem == '%d':
                day_col = pos
    
        if start_date is None:
            d = datetime.date.today()
        else:
            d = start_date
    
        self._year_value = tk.IntVar()
        self._year_value.set(d.year)
        self._year_entry = ttk.Entry(self, textvariable=self._year_value,
                                     width=4)
        self._year_entry.grid(row=0, column=year_col*2)

        self._month_value = tk.IntVar()
        self._month_value.set(d.month)
        self._month_entry = ttk.Entry(self, textvariable=self._month_value,
                                      width=2)
        self._month_entry.grid(row=0, column=month_col*2)

        self._day_value = tk.IntVar()
        self._day_value.set(d.day)
        self._day_entry = ttk.Entry(self, textvariable=self._day_value,
                                    width=2)
        self._day_entry.grid(row=0, column=day_col*2)
        
        lbl = ttk.Label(self, text=separator, width=1)
        lbl.grid(row=0, column=1)
        
        lbl = ttk.Label(self, text=separator, width=1)
        lbl.grid(row=0, column=3)
        
        btn = ttk.Button(self, text='Select...', command=self.select_date)
        btn.grid(row=0, column=5, sticky=tk.E)
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=1)

    def get(self):
        d = datetime.datetime(year=self._year_value.get(),
                              month=self._month_value.get(),
                              day=self._day_value.get())
        value = d.strftime(self.format)
        return value
    
    def set(self, value):
        value = str(value)
        d = datetime.datetime.strptime(value, self.format)
        self._year_value.set(d.year)
        self._month_value.set(d.month)
        self._day_value.set(d.day)

    def select_date(self):
        d = datetime.date(year=self._year_value.get(),
                          month=self._month_value.get(),
                          day=self._day_value.get())
        
        dlg = DateDialog(self._asker._root, 'Select a Date...', start_date=d)
        self._asker._root.wait_window(dlg._top)
        new_date = dlg.date
        if new_date != None:
            self._year_value.set(new_date.year)
            self._month_value.set(new_date.month)
            self._day_value.set(new_date.day)


class DateDialog(object):
    """Display a dialog to obtain a date from the user"""
    
    def __init__(self, master, title, start_date=None, font_size=-1):
        self._master = master
        self._top = tk.Toplevel(self._master)
        self._top.title(title)
        
        self._selector = DateSelector(self._top, start_date, font_size)
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
        self.ok_btn.grid(column=btn_column[0], row=0, padx=(6, 0))
        cancel = ttk.Button(okcancel, text='Cancel', width=10,
                            command=self._cancel)
        cancel.grid(column=btn_column[1], row=0, padx=(6, 0))

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
        self.date = self._selector.date
        self._top.grab_release()
        self._top.destroy()
    
    def _cancel(self, event=None):
        self.date = None
        self._top.grab_release()
        self._top.destroy()


class DateSelector(ttk.Frame):
    """A date selector widget which displays dates as a calendar, one
    month at a time.
    """
        
    FILL_COLOR_HEADER = '#ccc'
    FILL_COLOR_SELECT = '#82bdbd'
    TEXT_COLOR_OTHER_MONTH = '#888'
    
    def __init__(self, master, start_date=None, font_size=-1):
        self._master = master
        ttk.Frame.__init__(self, master)
        
        if start_date is None:
            self.date = datetime.date.today()
        else:
            self.date = start_date
        
        self._font_size = font_size
        
        self._rct_tag = ''
            
        self._calendar = calendar.TextCalendar()
        
        s = ttk.Style()
        s.configure('month.TLabel', font='TkDefaultFont', anchor='center')
        if self._font_size != -1:
            s.configure('month.TLabel', size=self._font_size)
        
        self._header = ttk.Frame(self, padding=(3,0))
        self._header.grid(row=0, column=0)
        
        self._prev_btn = ttk.Button(self._header, text='<', width=2,
                                    command=self._prev_month)
        self._prev_btn.grid(row=0, column=0, sticky=tk.E)
        
        self._month_year_lbl = ttk.Label(self._header, text='January',
                                         width=16, style='month.TLabel')
        self._month_year_lbl.grid(row=0, column=1, padx=5)
        
        self._next_btn = ttk.Button(self._header, text='>', width=2,
                                    command=self._next_month)
        self._next_btn.grid(row=0, column=2, sticky=tk.W)
        
        self._header.columnconfigure(0, weight=1)
        self._header.columnconfigure(1, weight=0)
        self._header.columnconfigure(2, weight=1)
        self.grid(row=0, column=0, sticky=(tk.N, tk.EW), padx=3, pady=3)
        self.columnconfigure(0, weight=1)
        
        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=1, column=0, columnspan=3)
        self._create()

        self._update()
        self._fill_date_rect()

    @property        
    def month(self):
        return self.date.month

    @month.setter        
    def month(self, month):
        self.date.month = month
        self._update()
    
    @property    
    def year(self):
        return self.date.year

    @year.setter        
    def year(self, year):
        self.date.year = year
        self._update()
    
    def set_year_and_month(self, year, month):
        self._year = year
        self._month = month
        self._update()
    
    def _create(self):
        week_days = self._calendar.formatweekheader(3).split(' ')
        
        day_font = font.Font(family='TkDefaultFont')
            
        item_width = max(day_font.measure(day) for day in week_days) + 1
        x_stride = item_width * 1.1

        item_height = day_font.metrics('linespace') + 3
        y_stride = item_height + 2
        
        half_width = int(item_width/2)
        half_height = int(item_height/2)
        x_start = x_stride
        y_start = y_stride
    
        x_pos = x_start
        y_pos = y_start
        
        rect_width = x_stride * 6.5
        self._canvas.create_rectangle(
            (x_start - half_width, y_start - half_height,
             x_start + rect_width, y_start + half_height),
            fill=self.FILL_COLOR_HEADER,
            outline='')
        
        for day in week_days:
            self._canvas.create_text((x_pos, y_pos), text=day,
                                     font='TkDefaultFont')
            x_pos = x_pos + x_stride
            
        y_pos += y_stride
        
        def _clicked(event):
            items = self._canvas.find_closest(event.x, event.y)
            tags = self._canvas.gettags(items[0])

            for tag in tags:
                if tag.startswith('day'):
                    break

            txt_tag = 'txt%s' % tag[3:]
            rct_tag = 'rct%s' % tag[3:]

            prev_rct_tag = self._rct_tag
            
            if prev_rct_tag:
                self._canvas.itemconfig(prev_rct_tag, fill='')
                
            self._canvas.itemconfig(rct_tag,
                                    fill=self.FILL_COLOR_SELECT)

            week_number, day_number = map(int, txt_tag[3:].split(':'))        
            self.date = self._get_date(week_number, day_number)

            self._rct_tag = rct_tag
        
        for week_number in range(6):
            x_pos = x_start
            for day_number in range(7):
                day_tag = 'day%d:%d' % (week_number,day_number)
                rct_tag = 'rct%d:%d' % (week_number,day_number)
                self._canvas.create_rectangle(
                    (x_pos - half_width,
                    y_pos - half_height,
                    x_pos + half_width,
                    y_pos + half_height),
                    outline='',
                    tags=(day_tag, rct_tag))
                
                text_tag = 'txt%d:%d' % (week_number,day_number)
                self._canvas.create_text((x_pos, y_pos-1), text='',
                                          tags=(day_tag, text_tag),
                                          font='TkDefaultFont')
                
                self._canvas.tag_bind(day_tag, '<Button-1>', _clicked)

                x_pos += x_stride
            y_pos += y_stride
        
        self._canvas.configure(width=x_pos, height=y_pos)
            
    def _update(self):
        """Redraw the calendar"""

        m = calendar.month_name[self.date.month]
        y = str(self.date.year)
        self._month_year_lbl['text'] = '%s, %s' % (m, y)
        
        self._days = self._calendar.monthdatescalendar(self.date.year,
                                                       self.date.month)

        if self._rct_tag:
            self._canvas.itemconfig(self._rct_tag, fill='')

        for week_number, days_in_week in enumerate(self._days):
            for day_number, date_ in enumerate(days_in_week):
                tag = 'txt%d:%d' % (week_number, day_number)
                text = str(date_.day)
                if self.date.month == date_.month:
                    self._canvas.itemconfigure(tag,
                                               text=text,
                                               fill='black')
                else:
                    self._canvas.itemconfigure(tag,
                                               text=text,
                                               fill=self.TEXT_COLOR_OTHER_MONTH)

                rct_tag = 'rct%s:%s' % (week_number, day_number)
                
                if self._rct_tag and rct_tag == self._rct_tag:
                    self._canvas.itemconfig(self._rct_tag, fill='')

                if self.date == date_:
                    self._canvas.itemconfig(rct_tag, 
                                            fill=self.FILL_COLOR_SELECT)
                    new_rct_tag = rct_tag
                    
        self._rct_tag = new_rct_tag
                
    def _next_month(self):
        self.date = next_month(self.date)
        self._update()

    def _prev_month(self):
        self.date = prev_month(self.date)
        self._update()

    def _get_date(self, week_number, day_number):
        return self._days[week_number][day_number]

    def _find_date_position(self, d):
        for week_number, week in enumerate(self._days):
            for day_number, day in enumerate(week):
                if day == d:
                    return (week_number, day_number)

    def _fill_date_rect(self):
        rct_tag = 'rct%d:%d' % self._find_date_position(self.date)

        self._canvas.itemconfig(rct_tag,
                                fill=self.FILL_COLOR_SELECT)

        self._rct_tag = rct_tag


def next_month(d):
    year = d.year
    month = d.month + 1
    if month > 12:
        year += 1
        month = 1
    
    try:
        return d.__class__(year=year, month=month, day=d.day)
    except ValueError:
        return d.__class__(year=year, month=month, day=1) - \
            datetime.timedelta(days=1)


def prev_month(d):
    year = d.year
    month = d.month - 1
    if month == 0:
        year -= 1
        month = 12
    
    try:
        return d.__class__(year=year, month=month, day=d.day)
    except ValueError:
        return d.__class__(year=year, month=month + 1, day=1) - \
            datetime.timedelta(days=1)
    