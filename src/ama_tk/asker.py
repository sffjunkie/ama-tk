# Copyright 2013-2014, Simon Kennedy, sffjunkie+code@gmail.com

"""Classes to ask questions using Tkinter

TkAsker
    The main class which generates the interface to ask the questions

TkQuestion
    The interface form a single question
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import os.path
import sys
import tkinter as tk
from collections import OrderedDict
from io import TextIOWrapper
from tkinter import font, ttk
from typing import Any

import ama.validator
import click
import tks.color_funcs
from ama.asker import Asker
from ama.hook.impl import hookimpl
from ama.types import Answers, Question, Result
from tks.colors import ColorEntry, ColorVar
from tks.dates import DateEntry, DateVar
from tks.fs import DirEntry
from tks.icon import set_icon_from_file, set_icon_from_resource
from tks.passwords import PasswordEntry
from tks.times import TimeEntry, TimeVar
from tks.tooltip import ToolTip


@hookimpl  # type: ignore
def ama_asker_class():
    return TkAsker


@hookimpl  # type: ignore
def ama_asker_addoption(command: click.Command) -> click.Command:
    option = click.option(
        "-i",
        "--invalid",
        "allow_invalid",
        is_flag=True,
        default=False,
        help="Return answers even if they don't validate",
    )
    return option(command)


class TkAsker(Asker):
    """Displays a Tk window containing the questions to be asked.

    :param title: The title to display
    :type title:     str
    :param preamble: Text to display before the questions
    :type preamble:  str
    :param filename: The filename from which to load a set of questions
    :type filename:  str
    :param allow_invalid: If True then invalid answers are accepted.
                          If False then you can't close the window until
                          all answers are valid.
    :type allow_invalid:  bool
    """

    def __init__(self, data: TextIOWrapper | str | None = None, **kwargs: Any):
        Asker.__init__(self, data)
        self._allow_invalid = kwargs.get("allow_invalid", False)
        self._create_root()
        self._ask: dict[str, Question] = {}

        self._row = 0
        self._working_directory = os.getcwd()
        self._result = None

    def add_question(self, question: Question) -> None:
        """Add a question to the list of questions.

        Called by the :meth:`Asker.ask` method or by your code.
        """

        tkq = TkQuestion(self, self._row, question)
        self._ask[question["name"]] = tkq
        self._row = self._row + 1

    def run(self):
        """Perform the question asking by displaying in a Tkinter window"""

        self._result = {}
        self._update_answers()
        self._root.update_idletasks()
        self._root.minsize(self._root.winfo_reqwidth(), self._root.winfo_reqheight())
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

    def _update_answers(self, update_info=None):
        """Update all unedited answers with the values from the other answers"""

        answers = self.current_answers(update_info)

        for key, tkq in self._ask.items():
            if (update_info is None or key != update_info[0]) and (
                not tkq.edited or key == update_info[0]
            ):
                tkq.update(answers)

    def check_invalid(self):
        """If we don't allow invalid answers then disable the OK button if
        we have any.
        """

        if not self._allow_invalid and not self._is_valid():
            self.ok_btn.state(["disabled"])
        else:
            self.ok_btn.state(["!disabled"])

        self.ok_btn.update_idletasks()

    def _create_root(self):
        self._root = tk.Tk()
        title = self.question_data["title"]
        preamble = self.question_data.get("preamble", None)

        self._root.title(title)

        set_icon_from_resource(self._root, "ama", "icon.gif")

        f = font.Font(font=("TkHeadingFont", 0, font.BOLD))
        ttk.Style().configure("header.TLabel", font=f)

        header = ttk.Label(self._root, text=preamble, padding=3, style="header.TLabel")
        header.grid(column=0, row=0, sticky=(tk.N, tk.EW))

        self.content_frame = ttk.Frame(self._root, padding=(3, 3, 3, 3))
        self.content_frame.grid(column=0, row=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        self.content_frame.columnconfigure(0, weight=0)
        self.content_frame.columnconfigure(1, weight=1)
        self.content_frame.columnconfigure(2, weight=0)

        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=0)

        okcancel = ttk.Frame(self._root, padding=(3, 3, 3, 3))

        # Swap the order of buttons for Windows
        if sys.platform.startswith("win32"):
            btn_column = (1, 2)
        else:
            btn_column = (2, 1)

        self.ok_btn = ttk.Button(okcancel, text="OK", width=10, command=self._ok)
        self.ok_btn.grid(column=btn_column[0], row=0, padx=(6, 0))
        cancel = ttk.Button(okcancel, text="Cancel", width=10, command=self._cancel)
        cancel.grid(column=btn_column[1], row=0, padx=(6, 0))

        okcancel.columnconfigure(0, weight=1)
        okcancel.columnconfigure(1, weight=0)
        okcancel.columnconfigure(2, weight=0)

        okcancel.grid(column=0, row=2, sticky=(tk.E, tk.W, tk.S))
        self._root.rowconfigure(2, weight=1)

        self._root.protocol("WM_DELETE_WINDOW", self._cancel)

        if sys.platform.startswith("darwin"):
            self._root.createcommand("::tk::mac::Quit", self._cancel)

    def _is_valid(self):
        """Check if all the answers are valid."""

        for _key, question in self._ask.items():
            if not question.valid:
                return False

        return True

    # pylint: disable=unused-argument
    def _ok(self, event=None):
        """Respond to the OK button being pressed."""

        self._result["valid"] = self._is_valid()
        self._result["result"] = "ok"

        answers = {}
        for key, tkq in self._ask.items():
            answers[key] = tkq.value

        self._result["answers"] = answers

        self._root.destroy()

    # pylint: disable=unused-argument
    def _cancel(self, event=None):
        """Respond to the Cancel button being pressed."""

        self._result["valid"] = False
        self._result["result"] = "cancel"
        self._root.destroy()


class TkQuestion(object):
    """Displays the controls for a single question."""

    def __init__(self, asker, row, question: Question):
        self._asker = asker
        self._row = row

        self._key = question["name"]
        self._label = question["message"]
        self._default = question.get("default", None)
        self._validator = question["type"]
        self._spec = question.get("format", None)

        if self._spec and self._spec.startswith("path"):
            self._default = os.path.normpath(self._default)

        self._dont_update = ["bool", "yesno", "date", "time", "color", "password"]

        self._tkvar = None
        self._entry = None

        self._is_edited = False
        self._is_valid = True

        f = font.Font(font=("TkTextFont",))
        ttk.Style().configure("question.TLabel", font=f)

        self.label = ttk.Label(
            asker.content_frame, text=self._label, style="question.TLabel"
        )
        self.label.grid(column=0, row=self._row, sticky=(tk.N, tk.S, tk.W), padx=(0, 5))

        ttk.Style().configure("error.TLabel", font=f)
        self._info_label = ttk.Label(asker.content_frame, width=2, anchor=tk.CENTER)
        self._info_label.grid(column=2, row=self._row, padx=(3, 0))

        self._help_text = question.get("help", "")
        if self._help_text != "":
            self._info_label["text"] = "?"
            ToolTip(self._info_label, msg=self._help_text, delay=0.5)

        self._validate_entry = (
            asker._root.register(self._tk_validate_entry),
            "%P",
            "%V",
        )

        current_answers = self._asker.current_answers()

        if self._validator == "path":
            self._tkvar = tk.StringVar()
            self._entry = DirEntry(asker.content_frame, variable=self._tkvar)
            frame = self._entry

        elif self._validator == "date":
            self._tkvar = DateVar()
            self._entry = DateEntry(asker.content_frame, variable=self._tkvar)
            frame = self._entry

        elif self._validator == "time":
            self._tkvar = TimeVar()
            self._entry = TimeEntry(asker.content_frame, variable=self._tkvar)
            frame = self._entry

        elif self._validator == "color":
            if self._spec:
                color_format = self._spec
            else:
                color_format = "rgbhex"

            self._tkvar = ColorVar()
            if self._default:
                if self._spec == "rgbhex":
                    color = tks.color_funcs.hex_string_to_rgb(self._default, True)
                else:
                    color = tks.color_funcs.color_string_to_rgb(self._default)

            self._tkvar.set(color)

            self._entry = ColorEntry(
                asker.content_frame, variable=self._tkvar, color_format=color_format
            )

            self._spec = "rgb"
            frame = self._entry

        elif self._validator == "password":
            self._tkvar = tk.StringVar()
            self._entry = PasswordEntry(asker.content_frame, variable=self._tkvar)
            frame = self._entry

        elif self._validator == "str":
            self._tkvar = tk.StringVar()
            self._entry = ttk.Entry(
                asker.content_frame,
                textvariable=self._tkvar,
                validate="all",
                validatecommand=self._validate_entry,
            )
            frame = self._entry

        elif self._validator == "int" or isinstance(self._validator, int):
            self._tkvar = tk.IntVar()
            self._entry = ttk.Entry(
                asker.content_frame,
                textvariable=self._tkvar,
                validate="all",
                validatecommand=self._validate_entry,
            )
            self._entry.configure(width=30)
            frame = self._entry

        elif self._validator == "float" or isinstance(self._validator, float):
            self._tkvar = tk.DoubleVar()
            self._entry = ttk.Entry(
                asker.content_frame,
                textvariable=self._tkvar,
                validate="all",
                validatecommand=self._validate_entry,
            )
            self._entry.configure(width=30)
            frame = self._entry

        elif (
            self._validator == "bool"
            or self._validator == "yesno"
            or isinstance(self._validator, bool)
        ):
            self._tkvar = tk.BooleanVar()
            self._tkvar.set(self._default or False)
            frame = ttk.Frame(asker.content_frame)

            if self._validator == "yesno":
                text = ("Yes", "No")
            else:
                text = ("True", "False")

            y = ttk.Radiobutton(frame, text=text[0], variable=self._tkvar, value=True)
            y.grid(column=0, row=0, padx=(0, 5))

            n = ttk.Radiobutton(frame, text=text[1], variable=self._tkvar, value=False)
            n.grid(column=1, row=0)

        elif isinstance(self._validator, list):
            self._tkvar = tk.StringVar()
            self.value = self._validator[0]
            if len(self._validator) <= 3:
                frame = ttk.Frame(asker.content_frame)
                for idx, e in enumerate(self._validator):
                    rb = ttk.Radiobutton(
                        frame, text=str(e), variable=self._tkvar, value=str(e)
                    )
                    rb.grid(column=idx, row=0, padx=(0, 5))
            else:
                self._entry = ttk.Combobox(
                    asker.content_frame, textvariable=self._tkvar
                )
                self._entry["values"] = tuple(self._validator)
                frame = self._entry

        else:
            raise ValueError(
                ("Unable to create entry widget " "for type %s") % self._validator
            )

        frame.grid(column=1, row=self._row, sticky=tk.EW, padx=0)

        asker.content_frame.rowconfigure(self._row, weight=1)
        self.edited = False

        self._validate = ama.validator.get_validator(self._validator, self._spec)

        if self._validator not in self._dont_update:
            self.update(current_answers)

    def update(self, current_answers):
        """Update our unedited value with the other answers."""

        if not self.edited and self._validator not in self._dont_update:
            _current_answers = {
                k: v for k, v in current_answers.items() if v is not None
            }

            if self._validator == "str" and self._default is None:
                self._default = ""
            updated_answer = str(self._default).format(**_current_answers)
            self.value = updated_answer

    @property
    def value(self):
        if self.valid:
            return self._validate(self._tkvar.get())
        else:
            return ""

    @value.setter
    def value(self, value):
        try:
            value = self._validate(value)
            self._tkvar.set(value)
            self.valid = True
        except (TypeError, ValueError):
            self._tkvar.set(value)
            self.valid = False

    @property
    def valid(self):
        return self._is_valid

    @valid.setter
    def valid(self, value):
        self._is_valid = bool(value)
        if self._is_valid:
            if self._help_text != "":
                self._info_label["text"] = "?"
            self._info_label["background"] = ""
        else:
            self._info_label["text"] = "!"
            self._info_label["background"] = "#e00"

    @property
    def edited(self):
        return self._is_edited

    @edited.setter
    def edited(self, value):
        self._is_edited = bool(value)

        if isinstance(self._entry, ttk.Entry):
            if self._is_edited:
                self._entry["style"] = "TEntry"
            else:
                self._entry["style"] = "unedited.TEntry"

    def _tk_validate_entry(self, P, V):
        # pylint: disable=invalid-name
        rtn = 1
        if V == "focusout":
            if self._spec == "nonempty" and not P:
                self.valid = False
                self.edited = True
            elif P.strip() == "":
                self.valid = True
                self.edited = False
            else:
                try:
                    _value = self._validate(P)
                    self.valid = True
                except (ValueError, TypeError):
                    self.valid = False
                    rtn = 0

            self._asker.check_invalid()
        elif V == "key":
            if not self.edited:
                self.edited = True

            self._asker._update_answers((self._key, P))

        return rtn

    def _create_entry_with_button(self, master, text, command):
        frame = ttk.Frame(master)

        self._entry = ttk.Entry(
            frame,
            textvariable=self._tkvar,
            validate="all",
            validatecommand=self._validate_entry,
        )
        self._entry.grid(column=0, row=0, sticky=tk.EW)

        btn = ttk.Button(frame, text=text, command=command)
        btn.grid(column=1, row=0, sticky=tk.E, padx=(6, 0))

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)

        return frame
