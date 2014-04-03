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


class DateEntry(ttk.Frame):
    """A date entry widget containing text entry boxes for year, month and day
    and a button to display a date selection dialog.
    
    :param master: The master frame
    :type master: :class:`ttk.Frame`
    :param start_date: The start date to display in the entry boxes
    :type start_date:  datetime.date or datetime.datetime
    :param date_separator: The string to display between the elements of the
                           entries.
    :type date_separator:  str
    :param first_day_of_week: The first day to display in the date selection
                              dialog
    :type first_day_of_week:  int
    """
    
    def __init__(self, master,
                 start_date=None,
                 date_separator='-',
                 first_day_of_week=calendar.MONDAY):
        super(DateEntry, self).__init__(master)

        self._calendar = calendar.LocaleTextCalendar(first_day_of_week, '')
    
        if start_date is None:
            d = datetime.date.today()
        elif not isinstance(d, (datetime.date, datetime.datetime)):
            raise ValueError('Invalid start date.')
        else:
            d = start_date
    
        self._time = None
        if isinstance(d, datetime.datetime):
            self._time = d.time()
    
        self._year_var = tk.IntVar()
        self._year_var.set(d.year)
        self._year_entry = ttk.Entry(self, textvariable=self._year_var,
                                     width=4)
        self._year_entry.grid(row=0, column=0)

        self._month_var = tk.IntVar()
        self._month_entry = ttk.Combobox(self,
                                         textvariable=self._month_var,
                                         width=3)
        self._month_entry['values'] = ['%02d' % (x + 1) for x in range(12)]
        self._month_var.set('%02d' % d.month)
        self._month_entry.grid(row=0, column=2)
        self._month_entry.bind('<<ComboboxSelected>>', self._month_updated)

        self._day_var = tk.IntVar()
        self._day_var.set('%02d' % d.day)
        self._day_entry = ttk.Combobox(self,
                                       textvariable=self._day_var,
                                       width=3)
        self._update_day_values(d.year, d.month)
        self._day_entry.grid(row=0, column=4)
        
        lbl = ttk.Label(self, text=date_separator, width=1)
        lbl.grid(row=0, column=1)
        
        lbl = ttk.Label(self, text=date_separator, width=1)
        lbl.grid(row=0, column=3)
        
        btn = ttk.Button(self, text='Select...', command=self.select_date)
        btn.grid(row=0, column=5, sticky=tk.E)
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=1)
        
    def _update_day_values(self, year, month):
        _, days_in_month = calendar.monthrange(year, month)
        
        new_day = None
        if self._day_entry['values']:
            current_last_day = int(self._day_entry['values'][-1])
            if current_last_day > days_in_month:
                new_day = days_in_month

        self._day_entry['values'] = ['%02d' % (x + 1) for x in range(days_in_month)]
        
        if new_day:
            self._day_var.set('%02d' % new_day)
            
    def _month_updated(self, event=None):
        self._update_day_values(self._year_var.get(), self._month_var.get())
        
    def get(self):
        d = datetime.datetime(year=self._year_var.get(),
                              month=self._month_var.get(),
                              day=self._day_var.get())
        
        if self._time:
            d = d.replace(hour=self._time.hour,
                          minute=self._time.minute,
                          second=self._time.second)
        
        return d
    
    def set(self, d):
        self._year_var.set(d.year)
        self._month_var.set('%02d' % d.month)
        self._day_var.set('%02d' % d.day)
        
        if isinstance(d, datetime.datetime):
            self._time = d.time()
        else:
            self._time = None

    def select_date(self):
        d = datetime.date(year=self._year_var.get(),
                          month=self._month_var.get(),
                          day=self._day_var.get())
        
        dlg = DateDialog(self, 'Select a Date...', start_date=d)
        self.wait_window(dlg)
        new_date = dlg.date
        if new_date != None:
            self.set(new_date)


class DateDialog(tk.Toplevel):
    """Display a dialog to obtain a date from the user"""
    
    def __init__(self, master, title, start_date=None, font_size=-1):
        super(DateDialog, self).__init__(master)
        self.title(title)
        
        self._selector = DateSelector(self, start_date, font_size)
        self._selector.grid(row=0, column=0, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        
        okcancel = ttk.Frame(self, padding=(3,3,3,3))
        
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
        
        self.resizable(width=False, height=False)
        
        self.bind('<Escape>', self._cancel)
        self.protocol('WM_DELETE_WINDOW', self._cancel)
        self.focus()
        self.transient(master)
        self.grab_set()

    def _ok(self, event=None):
        self.date = self._selector.date
        self.grab_release()
        self.destroy()
    
    def _cancel(self, event=None):
        self.date = None
        self.grab_release()
        self.destroy()


class DateSelector(ttk.Frame):
    """A date selector widget which displays dates as a calendar, one
    month at a time.
    """
        
    FILL_COLOR_HEADER = '#ccc'
    FILL_COLOR_SELECT = '#72e8f1'
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
        
        self._month_year_lbl = ttk.Label(self._header,
                                         width=16, style='month.TLabel')
        self._month_year_lbl.grid(row=0, column=1, padx=8)
        
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
        week_days = self._calendar.formatweekheader(3).split()
        
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
        
        # We display 6 weeks of days but some months only have 5 weeks in
        # them this means the calendar doesn't have the required number of rows
        # so we add another
        if len(self._days) == 5:
            d = self._days[4][-1]
            delta = datetime.timedelta(days=1)
            
            missing_days = []
            for day_number in range(7):
                d += delta
                missing_days.append(d)
            
            self._days.append(missing_days)

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
        return d.__class__(year=year, month=month + 1, day=1) - \
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
    