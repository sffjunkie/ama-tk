# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import os.path
import datetime
import gettext
from collections import OrderedDict

import wx

try:
    from tkinter import font
except ImportError:
    import tkFont as font

try:
    from tkinter import ttk
except ImportError:
    import ttk

from ama import Asker
import ama.validator
#from tks.icon import set_icon_from_resource, set_icon_from_file
#from tks.tooltip import ToolTip
#from tks.dates import DateVar, DateEntry
#from tks.times import TimeVar, TimeEntry
#from tks.colors import ColorVar, ColorEntry
#from tks.fs import DirEntry
#from tks.password import PasswordEntry
import tks.color_funcs


class WxAsker(Asker):
    """Displays a Tk window containing the questions to be asked.

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

    def __init__(self, title, preamble='', ds=None, json_string=None,
                 allow_invalid=True, icon=None):
        Asker.__init__(self, ds, json_string)
        self._preamble = preamble
        self._allow_invalid = allow_invalid
        self._ask = OrderedDict()
        self._working_directory = os.getcwd()
        self._row = 0

        self._dlg = wx.Dialog(None, wx.ID_ANY, title,
                              style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        #self._dlg.SetIcon()
        #if not icon:
        #    set_icon_from_resource(self._root, 'ama', 'icon.gif')
        #else:
        #    if isinstance(icon, tuple):
        #        set_icon_from_resource(self._root, *icon)
        #    else:
        #        set_icon_from_file(self._root, str(icon))

        root_sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.StaticText(self._dlg, label=self._preamble)
        f = header.GetFont()
        f.SetWeight(wx.FONTWEIGHT_BOLD)
        header.SetFont(f)
        root_sizer.Add(header, flag=wx.EXPAND | wx.ALL, border=3)

        self.content = wx.Panel(self._dlg)
        self.content_sizer = wx.FlexGridSizer(cols=3, hgap=3, vgap=3)
        self.content_sizer.AddGrowableCol(1)
        self.content_sizer.SetFlexibleDirection(wx.BOTH)
        self.content.SetSizer(self.content_sizer)
        self.content_sizer.Fit(self.content)

        root_sizer.Add(self.content_sizer, proportion=1,
                       flag=wx.EXPAND | wx.ALL, border=3)

        button_sizer = self._dlg.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        root_sizer.Add(button_sizer, flag=wx.EXPAND | wx.ALL, border=3)

        self._dlg.SetSizer(root_sizer)

    def add_question(self, key, question):
        """Add a question to the list of questions.

        Called by the :meth:`Asker.ask` method or by your code.
        """

        wxq = WxQuestion(self, self._row, question)
        self._ask[key] = wxq
        self._row += 1

    def go(self, initial_answers):
        """Perform the question asking by displaying in a wxPython window"""

        app = wx.App()

        self._result = {}
        self._update_answers()
        rc = self._dlg.ShowModal()
        if rc == wx.ID_OK:
            self._ok()
        else:
            self._cancel()

        app.Exit()

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

    def _update_answers(self, update_info=None):
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

    def _ok(self):
        """Respond to the OK button being pressed."""

        self._result['valid'] = self._is_valid()
        self._result['result'] = 'ok'

        answers = {}
        for key, tkq in self._ask.items():
            answers[key] = tkq.value

        self._result['answers'] = answers

    def _cancel(self):
        """Respond to the Cancel button being pressed."""

        self._result['valid'] = False
        self._result['result'] = 'cancel'


class WxQuestion(object):
    """Displays the controls for a single question."""

    def __init__(self, asker, row, question):
        self._asker = asker

        self._key = question.key
        self._default = question.default
        self._validator = question.validator
        self._spec = question.spec

        if self._spec and self._spec.startswith('path'):
            self._default = os.path.normpath(self._default)

        self._dont_update = ['date', 'time', 'color', 'password']

        self._value = None
        self._entry = None

        self._is_edited = False
        self._is_valid = True

        current_answers = self._asker.current_answers()

        self._info_label = wx.StaticText(asker.content, label=question.label)
        asker.content_sizer.Add(self._info_label, 0, wx.ALL | wx.EXPAND)

        #self.entry = wx.TextCtrl(asker.content)
        #asker.content_sizer.Add(self.entry, 1, wx.EXPAND | wx.ALL)

        self._add_entry(asker)

        self.help_text = wx.StaticText(asker.content, label='')
        asker.content_sizer.Add(self.help_text)

        self._help_text = question.help_text
        if self._help_text != '':
            self.help_text.SetLabel('?')
            tt = wx.ToolTip(self._help_text)
            self.help_text.SetToolTip(tt)

        self._validate = ama.validator.get_validator(self._validator,
                                                     self._spec)

        self.edited = False

    def update(self, current_answers):
        """Update our unedited value with the other answers."""

        if not self.edited and self._validator not in self._dont_update:
            updated_answer = str(self._default).format(**current_answers)
            self.value = updated_answer

    @property
    def value(self):
        if self.valid:
            return self._value
        else:
            return ''

    @value.setter
    def value(self, value):
        try:
            value = self._validate(value)
            self._value = value
            self.valid = True
        except (TypeError, ValueError):
            self._value = value
            self.valid = False

    @property
    def valid(self):
        return self._is_valid

    @valid.setter
    def valid(self, value):
        self._is_valid = bool(value)
        if self._is_valid:
            if self._help_text != '':
                self.help_text.SetLabel('?')
            #self._info_label['background'] = ''
        else:
            self.help_text.SetLabel('!')
            #self._info_label['background'] = '#e00'

    @property
    def edited(self):
        return self._is_edited

    @edited.setter
    def edited(self, value):
        self._is_edited = bool(value)

        if isinstance(self._entry, ttk.Entry):
            if self._is_edited:
                self._entry['style'] = 'TEntry'
            else:
                self._entry['style'] = 'unedited.TEntry'

    def _tk_validate_entry(self, P, V):
        rtn = 1
        if V == 'focusout':
            if self._spec == 'nonempty'and not P:
                self.valid = False
                self.edited = True
            elif P.strip() == '':
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

            self._asker._update_answers((self._key, P))

        return rtn

    def _add_entry(self, asker):
        if self._validator == 'path':
            self._value = ''
            self._entry = wx.TextCtrl(asker.content)
        elif self._validator == 'date':
            self._value = datetime.date.today()
            self._entry = wx.TextCtrl(asker.content)
        elif self._validator == 'time':
            self._value = datetime.datetime.now().time()
            self._entry = wx.TextCtrl(asker.content)
        elif self._validator == 'color':
            if self._spec:
                color_format = self._spec
            else:
                color_format = 'rgbhex'
            if self._default:
                if self._spec == 'rgbhex':
                    color = tks.color_funcs.hex_string_to_rgb(self._default,
                        True)
                else:
                    color = tks.color_funcs.color_string_to_rgb(self._default)
            self._value = color
            self._entry = wx.TextCtrl(asker.content)
        elif self._validator == 'password':
            self._value = ''
            self._entry = wx.TextCtrl(asker.content)
        elif self._validator == 'str':
            self._value = ''
            self._entry = wx.TextCtrl(asker.content)
        elif self._validator == 'int' or isinstance(self._validator, int):
            self._value = 0
            self._entry = wx.TextCtrl(asker.content)
        elif self._validator == 'float' or isinstance(self._validator, float):
            self._value = 0.0
            self._entry = wx.TextCtrl(asker.content)
        elif self._validator == 'bool' or self._validator == 'yesno' or isinstance(self._validator, bool):
            self._value = False
            self._entry = wx.TextCtrl(asker.content)
            #frame = wx.Window(asker.content)
            #if self._validator == 'yesno':
            #    text = 'Yes', 'No'
            #else:
            #    text = 'True', 'False'
            #y = ttk.Radiobutton(frame, text=text[0],
            #    variable=self._value, value=True)
            #y.grid(column=0, row=0, padx=(0, 5))
            #n = ttk.Radiobutton(frame, text=text[1],
            #    variable=self._value, value=False)
            #n.grid(column=1, row=0)
        elif isinstance(self._validator, list):
            self._value = []
            self._entry = wx.TextCtrl(asker.content)
            #self.value = self._validator[0]
            #if len(self._validator) <= 3:
            #    frame = ttk.Frame(asker.content_sizer)
            #    for idx, e in enumerate(self._validator):
            #        rb = ttk.Radiobutton(frame, text=str(e), variable=self._value, value=str(e))
            #        rb.grid(column=idx, row=0, padx=(0, 5))

            #else:
            #    self._entry = ttk.Combobox(asker.content_sizer,
            #        textvariable=self._value)
            #    self._entry['values'] = tuple(self._validator)
            #    frame = self._entry
        else:
            raise ValueError(
                ('Unable to create entry widget '
                    'for type %s') %
                self._validator)

        asker.content_sizer.Add(self._entry, flag=wx.EXPAND | wx.ALL)
