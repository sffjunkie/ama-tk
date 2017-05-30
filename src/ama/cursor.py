"""Terminal cursor control via ANSI escape sequences"""

import atexit
import sys

__all__ = ['toggle', 'show', 'hide']
_HIDDEN = False

def show():
    """Show the cursor"""
    _HIDDEN = False
    sys.stdout.write('\u001b[?25h')

def hide():
    """Hide the cursor"""
    _HIDDEN = True
    sys.stdout.write('\u001b[?25l')

def toggle(force=None):
    """Toggle the cursor"""
    if force is not None:
        _HIDDEN = force
    if _HIDDEN:
        show()
    else:
        hide()

atexit.register(show)
