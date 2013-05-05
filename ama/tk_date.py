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
from dateutil.relativedelta import relativedelta

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


class DateDialog(object):
    def __init__(self, master, title, start_date=None, font_size=10):
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
        self._top.grab_release()
        self._top.destroy()
        self.date = self._selector._date
    
    def _cancel(self, event=None):
        self._top.grab_release()
        self._top.destroy()
        self.date = None

class DateSelector(ttk.Frame):
    FILL_COLOR_HEADER = '#ccc'
    FILL_COLOR_ACTIVE = '#96c8c8'
    FILL_COLOR_SELECT = '#82bdbd'
    TEXT_COLOR_OTHER_MONTH = '#888'
    
    def __init__(self, master, start_date=None, font_size=10):
        """Create a DateSelector widget"""
        
        self._master = master
        ttk.Frame.__init__(self, master)
        
        self._font_size = font_size
        
        self._txt_tag = ''
        self._rct_tag = ''
            
        self._calendar = calendar.TextCalendar()
        
        self._style = ttk.Style()
        self._style.configure('month.TLabel', anchor='center')
        
        self._header = ttk.Frame(self, padding=(3,0))
        self._header.grid(row=0, column=0)
        
        self._prev_btn = ttk.Button(self._header, text='<', width=2,
                                    command=self._prev_month)
        self._prev_btn.grid(row=0, column=0, sticky=tk.E)
        
        month_font = font.Font(family='TkTextFont', weight='bold',
                               size=self._font_size)
        
        self._month_year_lbl = ttk.Label(self._header, text='January',
                                         width=16, style='month.TLabel',
                                         font=month_font)
        self._month_year_lbl.grid(row=0, column=1, padx=5)
        
        self._next_btn = ttk.Button(self._header, text='>', width=2,
                                    command=self._next_month)
        self._next_btn.grid(row=0, column=2, sticky=tk.W)
        
        self._header.columnconfigure(0, weight=1)
        self._header.columnconfigure(1, weight=0)
        self._header.columnconfigure(2, weight=1)
        self.grid(row=0, column=0, sticky=(tk.N, tk.EW))
        self.columnconfigure(0, weight=1)
        
        self._canvas = tk.Canvas(self)
        self._canvas.grid(row=1, column=0, columnspan=3)
        self._create()
        
        if start_date is None:
            self._date = datetime.date.today()
        else:
            self._date = start_date

        self._update()
        self._fill_date_rect()
        
    def month():
        def fget(self):
            return self._date.month
        
        def fset(self, month):
            self._date.month = month
            self._update()
            
        return locals()
    
    month = property(**month())
        
    def year():
        def fget(self):
            return self._date.year
        
        def fset(self, year):
            self._date.year = year
            self._update()
            
        return locals()
    
    year = property(**year())
    
    def set_year_and_month(self, year, month):
        self._year = year
        self._month = month
        self._update()
    
    def _update_month_year(self):
        m = calendar.month_name[self._date.month]
        y = str(self._date.year)
        self._month_year_lbl['text'] = '%s, %s' % (m, y)
    
    def _create(self):
        week_days = self._calendar.formatweekheader(3).split(' ')
        
        day_font = font.Font(family='TkTextFont', size=self._font_size)
        item_width = max(day_font.measure(day) for day in week_days)
        x_stride = item_width + 1

        item_height = day_font.metrics('linespace') + 3
        y_stride = item_height + 3
        
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
            self._canvas.create_text((x_pos, y_pos), text=day, font=day_font)
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

            prev_txt_tag = self._txt_tag
            prev_rct_tag = self._rct_tag
            
            if prev_rct_tag != '':
                self._canvas.itemconfig(prev_rct_tag, fill='')
                
            self._canvas.itemconfig(rct_tag,
                                    fill=self.FILL_COLOR_SELECT)

            week_number, day_number = map(int, txt_tag[3:].split(':'))        
            self._date = self._get_date(week_number, day_number)

            self._txt_tag = txt_tag
            self._rct_tag = rct_tag
        
        for week_number in range(5):
            x_pos = x_start
            for day_number in range(7):
                day_tag = 'day%d:%d' % (week_number,day_number)
                rct_tag = 'rct%d:%d' % (week_number,day_number)
                rect_id = self._canvas.create_rectangle(
                    (x_pos - half_width,
                    y_pos - half_height,
                    x_pos + half_width,
                    y_pos + half_height),
                    outline='',
                    tags=[day_tag, rct_tag])
                
                text_tag = 'txt%d:%d' % (week_number,day_number)
                text_id = self._canvas.create_text((x_pos, y_pos-1), text='',
                                              tags=[day_tag, text_tag],
                                              font=day_font)
                
                self._canvas.tag_bind(day_tag, '<Button-1>', _clicked)

                x_pos += x_stride
            y_pos += y_stride
        
        self._canvas.configure(width=x_pos, height=y_pos)
            
    def _update(self):
        """Redraw the calendar"""

        self._update_month_year()
        
        self._days = self._calendar.monthdatescalendar(self._date.year,
                                                       self._date.month)
        
        for week_number, days_in_week in enumerate(self._days):
            for day_number, date_ in enumerate(days_in_week):
                tag = 'txt%d:%d' % (week_number, day_number)
                text = str(date_.day)
                if self._date.month == date_.month:
                    self._canvas.itemconfigure(tag,
                                               text=text,
                                               fill='black')
                else:
                    self._canvas.itemconfigure(tag,
                                               text=text,
                                               fill=self.TEXT_COLOR_OTHER_MONTH)
        
    def _next_month(self):
        self._date += relativedelta(months=1)
        self._update()
        
    def _prev_month(self):
        self._date -= relativedelta(months=1)
        self._update()

    def _get_date(self, week_number, day_number):
        return self._days[week_number][day_number]
    
    def _find_date_position(self, d):
        for week_number, week in enumerate(self._days):
            for day_number, day in enumerate(week):
                if day == d:
                    return (week_number, day_number)
    
    def _fill_date_rect(self):
        rct_tag = 'rct%d:%d' % self._find_date_position(self._date)
                
        self._canvas.itemconfig(rct_tag,
                                fill=self.FILL_COLOR_SELECT)
        
        self._rct_tag = rct_tag
         